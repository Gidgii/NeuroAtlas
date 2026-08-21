#!/usr/bin/env python3
import http.server
import json
import socket
import threading
from functools import partial
from pathlib import Path

ROOT = Path(__file__).parents[1]
APP = ROOT / "app"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def capture_console_errors(error_list):
    def handle_console(msg):
        if msg.type == "error":
            error_list.append(msg.text)

    return handle_console


def accept_acknowledgement_gate(page):
    boxes = page.locator("[data-ack]")
    count = boxes.count()

    if count != 4:
        raise AssertionError(f"Expected four acknowledgement checkboxes, found {count}")

    form = boxes.first.locator("xpath=ancestor::form[1]")
    if form.count() != 1:
        raise AssertionError("Acknowledgement checkboxes are not inside one form")

    # Attempt submission before acknowledging anything.
    # A compliant gate must refuse to record acceptance.
    form.evaluate("form => form.requestSubmit()")
    page.wait_for_timeout(40)

    blocked_before_complete = not bool(
        page.evaluate("localStorage.getItem('neuroatlas-acknowledgement')")
    )

    for index in range(count):
        boxes.nth(index).check()

    form.evaluate("form => form.requestSubmit()")
    page.wait_for_timeout(100)

    raw = page.evaluate("localStorage.getItem('neuroatlas-acknowledgement')")
    record = json.loads(raw) if raw else {}

    gate_closed = not form.is_visible()

    return {
        "checkboxes": count,
        "blockedBeforeComplete": blocked_before_complete,
        "recordPersisted": bool(raw),
        "noticeVersion": record.get("noticeVersion"),
        "acceptedAt": bool(record.get("acceptedAt")),
        "storageModel": record.get("storageModel"),
        "gateClosed": gate_closed,
    }


def main():
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(f"P8 browser QA requires Playwright: {exc}")
        return 1

    port = free_port()
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(APP))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    checks = []

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for width, height, label in (
                (390, 844, "mobile"),
                (820, 1180, "tablet"),
                (1440, 900, "desktop"),
            ):
                page = browser.new_page(viewport={"width": width, "height": height})
                errors = []
                page.on("console", capture_console_errors(errors))
                page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")

                gate = accept_acknowledgement_gate(page)

                gate_ok = (
                    gate["checkboxes"] == 4
                    and gate["blockedBeforeComplete"]
                    and gate["recordPersisted"]
                    and gate["noticeVersion"] == "2026-08-21.1"
                    and gate["acceptedAt"]
                    and gate["storageModel"] == "local-device-only"
                    and gate["gateClosed"]
                )

                # The notice is versioned. An outdated acceptance must force
                # the user through acknowledgement again.
                stale_reprompt = True
                if label == "desktop":
                    page.evaluate(
                        """() => {
                            const key = 'neuroatlas-acknowledgement';
                            const record = JSON.parse(localStorage.getItem(key));
                            record.noticeVersion = 'stale-qa-version';
                            localStorage.setItem(key, JSON.stringify(record));
                        }"""
                    )
                    page.reload(wait_until="networkidle")
                    stale_reprompt = page.locator("[data-ack]").count() == 4
                    if stale_reprompt:
                        accept_acknowledgement_gate(page)

                page.wait_for_selector("#betaFeedbackButton")
                page.wait_for_selector('[data-release-dialog="disclaimerDialog"]')

                # The disclaimer must remain accessible after acceptance.
                page.click('[data-release-dialog="disclaimerDialog"]')
                disclaimer_open = page.locator("#disclaimerDialog").evaluate(
                    "dialog => dialog.open"
                )
                page.locator('#disclaimerDialog button[aria-label^="Close"]').click()
                page.click("#betaFeedbackButton")
                assert page.locator("#betaFeedbackDialog").evaluate("el => el.open")
                assert page.evaluate("window.NeuroAtlasReleaseCandidate.release") == "1.0.0-rc1"
                checks.append(
                    {
                        "viewport": label,
                        "pass": (not errors and gate_ok and stale_reprompt and disclaimer_open),
                        "acknowledgementGate": gate,
                        "staleVersionReprompt": stale_reprompt,
                        "disclaimerAccessibleAfterAcceptance": disclaimer_open,
                        "consoleErrors": errors,
                    }
                )
                page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    passed = all(check["pass"] for check in checks)
    print(json.dumps({"status": "PASS" if passed else "FAIL", "checks": checks}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
