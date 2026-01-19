"""
Simple HTTP Server for Frontend Dashboard

Run this to serve the frontend dashboard on http://localhost:3000
"""

import http.server
import socketserver
from pathlib import Path
import os

# Change to frontend directory
frontend_dir = Path(__file__).parent
os.chdir(frontend_dir)

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 Frontend Dashboard running at:")
        print(f"   http://localhost:{PORT}")
        print(f"\n✅ Make sure API server is running at http://localhost:8000")
        print(f"\nPress Ctrl+C to stop")
        httpd.serve_forever()
