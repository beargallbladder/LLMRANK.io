"""
Simple HTTP Server for LLMRank.io API Documentation

This server serves the terminal-themed API documentation on port 5000.
"""

import http.server
import socketserver
import os

PORT = 5000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/llmrank_api_docs.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

Handler = SimpleHTTPRequestHandler

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving LLMRank.io API docs at http://0.0.0.0:{PORT}")
        httpd.serve_forever()