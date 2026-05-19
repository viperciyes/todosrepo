#!/usr/bin/env python3
"""
Tiny dev server for todos.
- GET  /*        → serve static files from this directory
- POST /save     → write request body to tasks.json
"""
import http.server, json, os, sys

PORT = 8766
DIR  = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_POST(self):
        if self.path != '/save':
            self.send_error(404)
            return
        length = int(self.headers.get('Content-Length', 0))
        body   = self.rfile.read(length)
        # Validate JSON before writing
        try:
            json.loads(body)
        except json.JSONDecodeError as e:
            self.send_error(400, f'Invalid JSON: {e}')
            return
        path = os.path.join(DIR, 'tasks.json')
        with open(path, 'wb') as f:
            f.write(body)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, fmt, *args):
        # Suppress noisy GET logs, keep errors
        if args and str(args[1]) not in ('200', '304'):
            super().log_message(fmt, *args)

if __name__ == '__main__':
    os.chdir(DIR)
    server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    print(f'todos server → http://127.0.0.1:{PORT}/todos.html')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nstopped.')
