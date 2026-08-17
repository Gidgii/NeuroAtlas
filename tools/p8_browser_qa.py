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
                page.wait_for_selector("#betaFeedbackButton")
                page.click("#betaFeedbackButton")
                assert page.locator("#betaFeedbackDialog").evaluate("el => el.open")
                assert page.evaluate("window.NeuroAtlasReleaseCandidate.release") == "1.0.0-rc1"
                checks.append(
                    {
                        "viewport": label,
                        "pass": not errors,
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
