import http.server
import socketserver
import os

PORT = 8000
# 서버 스크립트의 위치를 기준으로 web_visualizer 디렉토리를 찾음
DIRECTORY = os.path.join(os.path.dirname(__file__), "web_visualizer")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

print(f"Serving files from: {os.path.abspath(DIRECTORY)}")
print(f"Access the visualizer at: http://localhost:{PORT}")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()