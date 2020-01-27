from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.parse import parse_qs
import json

PORT = 7604

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.make_data()
    def do_GET(self):
        if self.path == '/':
            self.path = '/web/index.html'
            try:
                file_to_open = open(self.path[1:]).read()
                self.send_response(200)
            except:
                file_to_open = "File Not Found"
                self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        else: self.make_data()
    def make_data(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        body = json.dumps({"cod":[0.22,0.88,0.982]})
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Content-length', len(body.encode()))
        self.end_headers()
        self.wfile.write(body.encode())

httpd = HTTPServer(("", PORT), MyHandler)
print('serving at port:%s' % PORT)
httpd.serve_forever()