#!/usr/bin/env python3
"""Focused browser smoke test for P6-P7 assessment and educator tooling."""

from __future__ import annotations

import shutil
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


def find_chromium() -> str | None:
    for candidate in (
        "chromium",
        "chromium-browser",
        "google-chrome",
        "google-chrome-stable",
    ):
        if path := shutil.which(candidate):
            return path
    return None


def main() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright is required for P6-P7 browser QA.") from exc

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(APP)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/"
    errors: list[str] = []

    try:
        with sync_playwright() as playwright:
            launch: dict[str, object] = {"headless": True}
            if executable := find_chromium():
                launch["executable_path"] = executable
            browser = playwright.chromium.launch(**launch)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on(
                "console",
                lambda message: errors.append(message.text) if message.type == "error" else None,
            )
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_selector("#assessmentButton", timeout=15000)
            page.click("#assessmentButton")
            page.wait_for_selector("#assessmentStudio[open]")
            assert page.locator("#assessmentStudio [data-case-id]").count() == 1

            page.locator('#assessmentStudio input[name="assessment-choice"]').first.check()
            page.locator('#assessmentStudio input[name="assessment-confidence"]').nth(2).check()
            submit = page.locator("#assessmentStudio [data-submit-assessment]")
            assert submit.is_enabled()
            submit.click()
            assert page.locator("#assessmentStudio [data-assessment-feedback]").is_visible()
            assert page.locator("#assessmentStudio .assessment-evidence").count() == 1

            page.locator("#assessmentStudio .dialog-head button").click()
            page.wait_for_selector("#educatorButton", timeout=5000)
            page.click("#educatorButton")
            page.wait_for_selector("#educatorStudio[open]")
            assert page.get_by_text("Export JSON").count() == 1
            assert page.get_by_text("Export CSV").count() == 1
            assert page.locator("#educatorStudio [data-pathway]").count() >= 7
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()

    print("P6/P7 browser QA: PASS")
    print("Assessment, confidence, evidence feedback and Educator Studio rendered successfully.")


if __name__ == "__main__":
    main()
