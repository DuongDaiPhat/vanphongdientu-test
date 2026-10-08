"""Isolated browser verification of the test code; never evidence about UTC."""

import html
import re
import secrets
import threading
import time
from dataclasses import replace
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from e2e.base.settings import Settings


class ReferenceServer:
    def __init__(self, defect="none"):
        self.defect = defect
        self.sessions = {}
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                return

            def do_GET(self):
                owner.respond(self, posted=False)

            def do_POST(self):
                owner.respond(self, posted=True)

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=3)

    def settings(self, root):
        settings = Settings.from_env(root)
        return replace(
            settings, base_url=f"http://127.0.0.1:{self.httpd.server_port}/Login", environment="test",
            error_selector="#error", authenticated_selector="#authenticated",
            patterns={"auth": r"Invalid username or password", "username": r"Username is required", "password": r"Password is required", "captcha": r"CAPTCHA (?:is required|is invalid|has expired|was already used)"},
            known_username="reference_existing_user", known_wrong_password="reference_wrong_password",
            captcha_image_selector="#challenge", captcha_refresh_selector="#refresh", captcha_ttl=1,
            captcha_ttl_margin=0.25, trigger_attempts=2, captcha_single_use=True,
            max_login_attempts=3, reset_selector="#reset", approved_test_host="127.0.0.1",
        )

    def url_for(self, test_name):
        case = re.search(r"tc\d{2}", test_name, re.I).group().upper()
        return f"http://127.0.0.1:{self.httpd.server_port}/Login?case={case}"

    def code_for(self, page, valid=True):
        sid = page.driver.get_cookie("reference_sid")["value"]
        code = self.sessions[sid]["code"]
        return code if valid else ("0" if code[0] != "0" else "1") + code[1:]

    @staticmethod
    def new_challenge(state):
        state.update(code=secrets.token_hex(3), issued=time.monotonic(), used=False, identity=secrets.token_hex(8))

    def respond(self, handler, posted):
        parsed = urlsplit(handler.path)
        query = parse_qs(parsed.query)
        if parsed.path == "/challenge.svg":
            # Browser needs a real image; the official test fixture supplies the code.
            content = b'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="24"><text x="2" y="18">test challenge</text></svg>'
            handler.send_response(200)
            handler.send_header("Content-Type", "image/svg+xml")
            handler.end_headers()
            handler.wfile.write(content)
            return
        cookies = SimpleCookie(handler.headers.get("Cookie", ""))
        sid = cookies["reference_sid"].value if "reference_sid" in cookies else secrets.token_hex(12)
        case = query.get("case", ["TC01"])[0]
        if sid not in self.sessions:
            self.sessions[sid] = {"case": case, "attempts": 0}
            self.new_challenge(self.sessions[sid])
        state = self.sessions[sid]
        if query.get("reset"):
            state["attempts"] = 0
            self.new_challenge(state)
        if query.get("refresh"):
            self.new_challenge(state)
        number = int(case[2:])
        captcha = number >= 13 and (number != 22 or state["attempts"] >= 2)
        error = ""
        authenticated = False
        if posted:
            data = parse_qs(handler.rfile.read(int(handler.headers.get("Content-Length", 0))).decode(), keep_blank_values=True)
            username, password, code = (data.get(key, [""])[0] for key in ("username", "userpwd", "captcha"))
            if captcha and self.defect != "captcha-bypass":
                if not code.strip():
                    error = "CAPTCHA is required"
                elif number == 17 and time.monotonic() - state["issued"] > 1:
                    error = "CAPTCHA has expired"
                elif number == 21 and state["used"]:
                    error = "CAPTCHA was already used"
                elif code != state["code"]:
                    error = "CAPTCHA is invalid"
            if not error:
                if not username.strip():
                    error = "Username is required"
                elif not password.strip():
                    error = "Password is required"
                else:
                    error = "Invalid username or password"
                if captcha:
                    state["used"] = True
            if self.defect == "authentication-bypass":
                authenticated = True
            if self.defect == "wrong-message":
                error = "Unrelated error, not the expected rejection"
            state["attempts"] += 1
            captcha = number >= 13 and (number != 22 or state["attempts"] >= 2)
        action = f"/Login?case={case}"
        captcha_fields = f'''<input type="hidden" name="spacer1"><input type="hidden" name="spacer2"><input type="hidden" name="spacer3"><input type="hidden" name="spacer4">
<input placeholder="Mã bảo mật" type="text" name="captcha">''' if captcha else '<input type="hidden" name="spacer1">'
        body = f'''<!doctype html><html><head><meta charset="utf-8"><title>Local reference form</title></head><body>
<div><div class="main"><div class="right"><div class="form">
<div id="error" role="alert">{html.escape(error)}</div>
<form method="post" action="{action}">
{captcha_fields}
<input placeholder="Tên đăng nhập" type="text" name="username">
<input placeholder="Mật khẩu" type="password" name="userpwd">
<input type="submit" class="submit_login" value="Đăng nhập">
</form>
<img id="challenge" src="/challenge.svg?id={state['identity']}" alt="Reference challenge">
<a id="refresh" href="{action}&amp;refresh=1">Refresh challenge</a>
<a id="reset" href="{action}&amp;reset=1">Reset test session</a>
{'<div id="authenticated">Authenticated</div>' if authenticated else ''}
</div></div></div></div></body></html>'''.encode("utf-8")
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.send_header("Set-Cookie", f"reference_sid={sid}; HttpOnly; SameSite=Lax; Path=/")
        handler.send_header("Cache-Control", "no-store")
        handler.end_headers()
        handler.wfile.write(body)
