"""
Thiep Chuc Mung 20/10 - Ngay Phu Nu Viet Nam
Chay: python server.py
Mo trinh duyet: http://localhost:8020

Chinh sua noi dung trong file: index.html
"""

import http.server
import socketserver
import os
import mimetypes
import json
import urllib.parse

PORT = 8021
HTML_FILE = "index.html"


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # API quét tự động danh sách file nhạc trong thư mục
        if parsed.path == "/api/songs":
            songs = []
            for fname in os.listdir(base_dir):
                if fname.lower().endswith((".mp3", ".wav", ".ogg", ".m4a")):
                    title = os.path.splitext(fname)[0].replace("-", " ").replace("_", " ").title()
                    songs.append({"title": title, "file": fname})
            songs.sort(key=lambda x: x["file"])
            data = json.dumps(songs, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # Nếu yêu cầu file tĩnh (file nhạc mp3, hình ảnh, v.v.)
        req_file = parsed.path.lstrip("/")
        if req_file:
            unquoted_file = urllib.parse.unquote(req_file)
            file_path = os.path.join(base_dir, unquoted_file)
            if os.path.isfile(file_path):
                # Tự phục vụ file trực tiếp với mime type chuẩn
                guessed_type, _ = mimetypes.guess_type(file_path)
                mime_type = guessed_type or ("audio/mpeg" if file_path.lower().endswith(".mp3") else "application/octet-stream")
                try:
                    file_size = os.path.getsize(file_path)
                    with open(file_path, "rb") as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", mime_type)
                    self.send_header("Content-Length", str(len(data)))
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b"Error reading file")
                    return

        # Mặc định trả về index.html
        html_path = os.path.join(base_dir, HTML_FILE)
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()
            data = content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File index.html khong tim thay!")

    def log_message(self, format, *args):
        print(f"  [Request] {args[0]}")


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print()
    print("  +-----------------------------------------------+")
    print("  |    THIEP CHUC MUNG 20/10                      |")
    print("  |    Ngay Phu Nu Viet Nam                       |")
    print("  +-----------------------------------------------+")
    print(f"  |    http://localhost:{PORT}                      |")
    print(f"  |    Chinh sua noi dung: {HTML_FILE}             |")
    print("  |    Nhan Ctrl+C de dung                        |")
    print("  +-----------------------------------------------+")
    print()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Tam biet! Hen gap lai~")
