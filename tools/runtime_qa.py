#!/usr/bin/env python3
"""Browser-level runtime QA for the Clinical Neuroscience Atlas.

Two transports are supported:
- injected: runs the real Atlas JavaScript + JSON inside an in-memory Chromium page.
  This is useful in locked-down CI/sandbox environments that prohibit localhost.
- http: serves app/ over a loopback HTTP server and tests the production loading path.

The checks intentionally exercise user-visible behaviour rather than internal functions.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
DATA = APP / "data"
REPORT_PATH = ROOT / "RUNTIME_QA_REPORT.json"

MODULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("spaced-repetition.js", ("SpacedRepetition",)),
    ("mastery-tracker.js", ("MasteryTracker",)),
    ("competency-tracker.js", ("CompetencyTracker", "COMPETENCIES")),
    ("calibration-tracker.js", ("CalibrationTracker", "CONFIDENCE_LEVELS")),
    ("deep-dive.js", ("renderDeepDiveButton", "bindDeepDive")),
    ("content-quality.js", ("renderContentQualitySummary", "searchableDetailText")),
    ("accessibility-runtime.js", ("focusMainHeading", "installAccessibilityRuntime")),
    ("visual-scenes.js", ("hasVisualScene", "renderVisualScene")),
    ("neuron-explorer.js", ("renderNeuronExplorer", "bindNeuronExplorer")),
    ("astrocyte-explorer.js", ("renderAstrocyteExplorer", "bindAstrocyteExplorer")),
    ("microglia-explorer.js", ("renderMicrogliaExplorer", "bindMicrogliaExplorer")),
    (
        "oligodendrocyte-explorer.js",
        ("renderOligodendrocyteExplorer", "bindOligodendrocyteExplorer"),
    ),
    ("system-explorer.js", ("renderSystemExplorer", "bindSystemExplorer")),
)


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class Report:
    transport: str
    started_at: float = field(default_factory=time.time)
    checks: list[Check] = field(default_factory=list)
    console_errors: list[str] = field(default_factory=list)
    page_errors: list[str] = field(default_factory=list)
    request_failures: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append(Check(name, ok, detail))

    @property
    def passed(self) -> int:
        return sum(c.ok for c in self.checks)

    @property
    def failed(self) -> int:
        return sum(not c.ok for c in self.checks)

    def as_dict(self) -> dict[str, Any]:
        return {
            "transport": self.transport,
            "duration_seconds": round(time.time() - self.started_at, 2),
            "summary": {"passed": self.passed, "failed": self.failed, "total": len(self.checks)},
            "metrics": self.metrics,
            "console_errors": self.console_errors,
            "page_errors": self.page_errors,
            "request_failures": self.request_failures,
            "checks": [c.__dict__ for c in self.checks],
        }


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _strip_exports(source: str) -> str:
    source = re.sub(r"\bexport\s+(?=(?:const|let|var|class|function)\b)", "", source)
    source = re.sub(r"\bexport\s*\{[^}]*\}\s*;?", "", source)
    return source


def _build_injected_bundle() -> str:
    chunks: list[str] = []
    for filename, exports in MODULES:
        source = _strip_exports((APP / filename).read_text(encoding="utf-8"))
        names = ", ".join(exports)
        chunks.append(f"const {{{names}}} = (() => {{\n{source}\nreturn {{{names}}};\n}})();")

    app_source = (APP / "app.js").read_text(encoding="utf-8")
    app_source = re.sub(r"^import\s+.*?;\s*$", "", app_source, flags=re.MULTILINE)
    chunks.append(app_source)
    return "\n\n".join(chunks)


def _build_injected_html() -> tuple[str, dict[str, str]]:
    html = (APP / "index.html").read_text(encoding="utf-8")
    html = re.sub(r'<script\s+type="module"\s+src="app\.js"\s*></script>', "", html)
    html = re.sub(r'<link\s+rel="stylesheet"\s+href="styles\.css"\s*/?>', "", html)
    css = (APP / "styles.css").read_text(encoding="utf-8")
    html = html.replace("</head>", f"<style>{css}</style></head>")
    payloads = {f"./data/{p.name}": p.read_text(encoding="utf-8") for p in DATA.glob("*.json")}
    return html, payloads


def _find_chromium(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for candidate in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        path = shutil.which(candidate)
        if path:
            return path
    return None


def _start_server() -> tuple[ThreadingHTTPServer, str]:
    handler = partial(QuietHandler, directory=str(APP))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/"


def _wait_for_app(page: Any) -> None:
    page.wait_for_function(
        "() => document.querySelectorAll('[data-level]').length > 0", timeout=15000
    )


def _safe_text(locator: Any) -> str:
    return (locator.text_content() or "").strip()


def run_qa(transport: str, executable_path: str | None = None, headless: bool = True) -> Report:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise SystemExit(
            "Playwright is required for runtime QA. Install with: pip install -e '.[runtime]'"
        ) from exc

    curriculum = _read_json(DATA / "curriculum.json")
    concepts = sorted(curriculum["concepts"], key=lambda item: (item["level"], item["order"]))
    report = Report(transport=transport)
    server: ThreadingHTTPServer | None = None

    with sync_playwright() as p:
        launch_kwargs: dict[str, Any] = {"headless": headless}
        chromium_path = _find_chromium(executable_path)
        if chromium_path:
            launch_kwargs["executable_path"] = chromium_path
        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900}, reduced_motion="reduce"
        )
        page = context.new_page()
        page.on(
            "console",
            lambda msg: report.console_errors.append(msg.text) if msg.type == "error" else None,
        )
        page.on("pageerror", lambda exc: report.page_errors.append(str(exc)))
        page.on(
            "requestfailed",
            lambda request: report.request_failures.append(f"{request.url}: {request.failure}"),
        )

        if transport == "http":
            server, url = _start_server()
            response = page.goto(url, wait_until="networkidle", timeout=15000)
            report.add(
                "HTTP entry point returns success",
                bool(response and response.ok),
                str(response.status if response else "no response"),
            )
        else:
            html, payloads = _build_injected_html()
            page.set_content(html, wait_until="domcontentloaded")
            page.evaluate(
                """payloads => {
                    const values = new Map();
                    const storage = {
                        getItem: key => values.has(String(key)) ? values.get(String(key)) : null,
                        setItem: (key, value) => values.set(String(key), String(value)),
                        removeItem: key => values.delete(String(key)),
                        clear: () => values.clear(),
                        key: index => [...values.keys()][index] ?? null,
                        get length() { return values.size; }
                    };
                    Object.defineProperty(window, 'localStorage', {value: storage, configurable: true});
                    window.fetch = async input => {
                        const key = String(input);
                        if (!(key in payloads)) return new Response('', {status: 404});
                        return new Response(payloads[key], {status: 200, headers: {'Content-Type': 'application/json'}});
                    };
                }""",
                payloads,
            )
            page.add_script_tag(content=_build_injected_bundle())

        try:
            _wait_for_app(page)
        except Exception as exc:
            report.add("Application initialises", False, str(exc))
            browser.close()
            if server:
                server.shutdown()
            return report

        report.add("Application initialises", True)
        report.add(
            "Home page has one primary heading",
            page.locator("main h1").count() == 1,
            _safe_text(page.locator("main h1").first),
        )
        report.add(
            "All curriculum levels render",
            page.locator("[data-level]").count() == len(curriculum["levels"]),
            f"rendered={page.locator('[data-level]').count()} expected={len(curriculum['levels'])}",
        )
        report.metrics["concepts"] = len(concepts)
        report.metrics["levels"] = len(curriculum["levels"])

        # Search flow and keyboard accessibility.
        page.keyboard.press("/")
        shortcut_open = page.locator("#searchDialog").evaluate("dialog => dialog.open")
        report.add("Slash shortcut opens search", bool(shortcut_open))
        page.locator('#searchDialog button[aria-label="Close search"]').click()
        page.click("#searchButton")
        page.fill("#searchInput", "amygdala")
        page.wait_for_timeout(50)
        search_count = page.locator("[data-search-open]").count()
        report.add("Search returns matching concepts", search_count > 0, f"results={search_count}")
        if search_count:
            page.locator("[data-search-open]").first.click()
            report.add(
                "Search result opens a concept",
                page.locator(".concept-header h1").count() == 1,
            )
            page.wait_for_timeout(50)
            focused_heading = page.evaluate(
                "() => document.activeElement === document.querySelector('.concept-header h1')"
            )
            report.add("Route changes move focus to the concept heading", bool(focused_heading))
            deep_dive = page.locator("[data-open-deep-dive]")
            deep_dive_available = deep_dive.count() == 1
            if deep_dive_available:
                deep_dive.click()
                dialog_open = page.locator("#deepDiveDialog").evaluate("dialog => dialog.open")
                page.locator("[data-close-deep-dive]").click()
            else:
                dialog_open = False
            report.add(
                "Deep dive opens as an accessible secondary layer",
                deep_dive_available and bool(dialog_open),
            )

        # Exhaustive concept render scan + visual scene checks. Run inside the page so the
        # full 249-concept sweep remains fast enough for routine regression testing.
        scan = page.evaluate(
            """concepts => concepts.map(concept => {
                const failures = [];
                window.openAtlasConcept(concept.id);
                const heading = document.querySelector('.concept-header h1')?.textContent?.trim() || '';
                if (heading !== concept.title) failures.push(`heading=${JSON.stringify(heading)}`);
                const body = document.querySelector('main')?.innerText || '';
                const hero = document.querySelector('.concept-hero');
                const visualButton = document.querySelector('[data-open-visual]');
                let visualOpened = null;
                if (visualButton) {
                    visualButton.click();
                    visualOpened = document.querySelectorAll('[data-visual-demo]').length === 1;
                    document.querySelector('[data-close-visual]')?.click();
                }
                return {
                    id: concept.id,
                    failures,
                    hasUndefined: /\bundefined\b/i.test(body),
                    hasAlt: !!(hero?.getAttribute('alt') || '').trim(),
                    hasVisual: !!visualButton,
                    visualOpened,
                    hasExplorer: !!document.querySelector('.neuron-explorer,.astro-explorer,.micro-explorer,.oligo-explorer,.system-explorer')
                };
            })""",
            [{"id": item["id"], "title": item["title"]} for item in concepts],
        )
        render_failures = [
            f"{item['id']}: {'; '.join(item['failures'])}" for item in scan if item["failures"]
        ]
        render_failures += [
            f"{item['id']}: visual scene did not open"
            for item in scan
            if item["hasVisual"] and not item["visualOpened"]
        ]
        undefined_concepts = [item["id"] for item in scan if item["hasUndefined"]]
        missing_alt = [item["id"] for item in scan if not item["hasAlt"]]
        visual_ids = [item["id"] for item in scan if item["hasVisual"]]
        explorer_ids = [item["id"] for item in scan if item["hasExplorer"]]

        report.metrics["visual_scene_count"] = len(visual_ids)
        report.metrics["explorer_count"] = len(explorer_ids)
        report.metrics["visual_scene_ids"] = visual_ids
        report.metrics["explorer_ids"] = explorer_ids
        report.add("Every concept renders", not render_failures, "; ".join(render_failures[:10]))
        report.add(
            "Rendered concepts contain no literal undefined",
            not undefined_concepts,
            ", ".join(undefined_concepts[:20]),
        )
        report.add("Every concept hero has alt text", not missing_alt, ", ".join(missing_alt[:20]))
        report.add(
            "Visual scenes open and close",
            not any("visual scene" in item for item in render_failures),
            f"scenes={len(visual_ids)}",
        )

        # Tabs on a representative concept.
        first = concepts[0]
        page.evaluate("id => window.openAtlasConcept(id)", first["id"])
        tab_count = page.locator("[role=tab]").count()
        report.add("Concept exposes all seven depth tabs", tab_count == 7, f"tabs={tab_count}")
        tab_failures: list[str] = []
        for i in range(tab_count):
            tab = page.locator("[role=tab]").nth(i)
            label = _safe_text(tab)
            tab.click()
            content = _safe_text(page.locator("[role=tabpanel] p"))
            if not content:
                tab_failures.append(label)
        report.add("All depth tabs contain content", not tab_failures, ", ".join(tab_failures))

        # Bookmark flow and persistence within the active origin/document.
        page.evaluate("id => window.openAtlasConcept(id)", first["id"])
        page.click("[data-bookmark]")
        bookmarked = page.locator("[data-bookmark].saved").count() == 1
        page.click("#bookmarkButton")
        listed = page.locator(f'[data-open="{first["id"]}"]').count() >= 1
        report.add("Bookmark saves and appears in Bookmarks", bookmarked and listed)

        # Quiz -> progress -> review flow. Start with clean app storage for deterministic answer selection.
        page.evaluate(
            "localStorage.removeItem('cna-progress'); localStorage.removeItem('cna-review-v1')"
        )
        page.reload() if transport == "http" else None
        if transport == "http":
            _wait_for_app(page)
        else:
            # State objects were created before storage was cleared. Recreate the page for a clean deterministic run.
            context.close()
            context = browser.new_context(
                viewport={"width": 1280, "height": 900}, reduced_motion="reduce"
            )
            page = context.new_page()
            page.on(
                "console",
                lambda msg: report.console_errors.append(msg.text) if msg.type == "error" else None,
            )
            page.on("pageerror", lambda exc: report.page_errors.append(str(exc)))
            html, payloads = _build_injected_html()
            page.set_content(html, wait_until="domcontentloaded")
            page.evaluate(
                """payloads => {
                    const values = new Map();
                    const storage = {
                        getItem: key => values.has(String(key)) ? values.get(String(key)) : null,
                        setItem: (key, value) => values.set(String(key), String(value)),
                        removeItem: key => values.delete(String(key)),
                        clear: () => values.clear(),
                        key: index => [...values.keys()][index] ?? null,
                        get length() { return values.size; }
                    };
                    Object.defineProperty(window, 'localStorage', {value: storage, configurable: true});
                    window.fetch = async input => {
                        const key=String(input); return key in payloads
                          ? new Response(payloads[key], {status:200, headers:{'Content-Type':'application/json'}})
                          : new Response('', {status:404});
                    };
                }""",
                payloads,
            )
            page.add_script_tag(content=_build_injected_bundle())
            _wait_for_app(page)

        page.evaluate("id => window.openAtlasConcept(id)", first["id"])
        page.click("[data-quiz]")
        detail_path = DATA / f"{first['id']}.json"
        detail = _read_json(detail_path) if detail_path.exists() else {}
        bank = detail.get("quizBank") or detail.get("quiz") or []
        question = bank[0] if bank else first["quiz"]
        answer_index = question.get("answer", question.get("correctAnswer"))
        page.locator("[data-answer]").nth(int(answer_index)).click()
        correct = page.locator(".answer-button.correct").count() == 1 and "Correct." in _safe_text(
            page.locator(".feedback")
        )
        report.add("Correct quiz answer is scored correctly", correct)
        progress_obj = page.evaluate("JSON.parse(localStorage.getItem('cna-progress') || '{}')")
        review_obj = page.evaluate("JSON.parse(localStorage.getItem('cna-review-v1') || '{}')")
        report.add(
            "Quiz completion persists to localStorage",
            bool(progress_obj.get(first["id"], {}).get("completed")),
        )
        report.add("Completed quiz enters review queue", first["id"] in review_obj)

        page.click('[data-route="review"]')
        review_visible = page.locator(".review-card").count() == 1
        if review_visible:
            confidence_buttons = page.locator("[data-confidence]")
            if confidence_buttons.count():
                confidence_buttons.nth(2).click()

            page.click("#revealReview")
            revealed = not page.locator("#reviewAnswer").is_hidden()
            page.locator('[data-grade="4"]').click()
            scheduled = page.locator(".review-empty").count() == 1
        else:
            revealed = scheduled = False
        report.add(
            "Review card can be revealed and graded", review_visible and revealed and scheduled
        )

        page.click('[data-route="progress"]')
        progress_text = _safe_text(page.locator("main"))
        report.add(
            "Progress page reflects completed concept",
            "1" in progress_text and "Concepts complete" in progress_text,
        )

        # Reduced-motion explorer sequence should complete synchronously rather than leaving a disabled control.
        run_tested = False
        run_ok = True
        run_detail = "no explorer with sequence control found"
        for cid in explorer_ids:
            page.evaluate("id => window.openAtlasConcept(id)", cid)
            if page.locator("[data-system-run]").count():
                run_tested = True
                page.click("[data-system-run]")
                run_ok = not page.locator("[data-system-run]").is_disabled()
                run_detail = cid
                break
        report.add(
            "Reduced-motion pathway sequence completes without locking controls",
            run_tested and run_ok,
            run_detail,
        )

        # Mobile viewport smoke test.
        page.set_viewport_size({"width": 390, "height": 844})
        page.evaluate("() => window.scrollTo(0,0)")
        page.click("#homeButton")
        overflow = page.evaluate(
            "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
        )
        report.add(
            "Home page has no material mobile horizontal overflow",
            overflow <= 2,
            f"overflow_px={overflow}",
        )
        page.click('[data-route="learn"]')
        overflow = page.evaluate(
            "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
        )
        report.add(
            "Learn page has no material mobile horizontal overflow",
            overflow <= 2,
            f"overflow_px={overflow}",
        )

        # Lightweight semantic/accessibility contracts.
        empty_named_buttons = page.evaluate(
            """() => [...document.querySelectorAll('button')].filter(b =>
                !(b.innerText || '').trim() && !(b.getAttribute('aria-label') || '').trim()
            ).length"""
        )
        report.add(
            "Visible buttons have text or an aria-label",
            empty_named_buttons == 0,
            f"unnamed={empty_named_buttons}",
        )

        # Browser-level error gates. Injected transport intentionally has no network requests for images.
        report.add(
            "No uncaught JavaScript exceptions",
            not report.page_errors,
            "; ".join(report.page_errors[:10]),
        )
        report.add(
            "No console error messages",
            not report.console_errors,
            "; ".join(report.console_errors[:10]),
        )
        if transport == "http":
            report.add(
                "No failed runtime requests",
                not report.request_failures,
                "; ".join(report.request_failures[:10]),
            )

        context.close()
        browser.close()

    if server:
        server.shutdown()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", choices=("injected", "http"), default="http")
    parser.add_argument("--chromium", help="Explicit Chromium/Chrome executable path")
    parser.add_argument("--headed", action="store_true", help="Show the browser window")
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    report = run_qa(args.transport, executable_path=args.chromium, headless=not args.headed)
    args.report.write_text(json.dumps(report.as_dict(), indent=2) + "\n", encoding="utf-8")

    for check in report.checks:
        marker = "PASS" if check.ok else "FAIL"
        suffix = f" â€” {check.detail}" if check.detail else ""
        print(f"[{marker}] {check.name}{suffix}")
    print(f"\nRuntime QA: {report.passed}/{len(report.checks)} passed; {report.failed} failed")
    print(f"Report: {args.report}")
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
