"""Receive a human's CAPTCHA answer for exactly one browser challenge."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Event
from uuid import uuid4


def wait_for_code(page, inbox, case, timeout):
    inbox = Path(inbox).resolve()
    inbox.mkdir(parents=True, exist_ok=True)
    request_id = uuid4().hex
    screenshot = inbox / (request_id + ".png")
    reply_path = inbox / (request_id + "-answer.json")
    request_path = inbox / "current-request.json"
    page.driver.save_screenshot(str(screenshot))
    challenge = {
        "request_id": request_id, "case": case, "status": "awaiting_answer",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "timeout_seconds": timeout, "screenshot": str(screenshot),
        "reply_path": str(reply_path),
    }

    def publish(status):
        challenge["status"] = status
        temporary = request_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(challenge, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(request_path)

    publish("awaiting_answer")
    print(f"\nCAPTCHA request for {case}: {request_path}", flush=True)
    deadline = time.monotonic() + timeout
    try:
        while time.monotonic() < deadline:
            if reply_path.is_file():
                try:
                    reply = json.loads(reply_path.read_text(encoding="utf-8-sig"))
                except (ValueError, OSError):
                    reply = None  # A writer may still be completing the file.
                if isinstance(reply, dict) and reply.get("request_id") == request_id:
                    code = reply.get("code")
                    if isinstance(code, str) and code.strip():
                        publish("consumed")
                        return code.strip()
            Event().wait(min(0.25, max(0, deadline - time.monotonic())))
        publish("expired")
        raise TimeoutError("No human CAPTCHA answer received for the current challenge")
    finally:
        reply_path.unlink(missing_ok=True)
