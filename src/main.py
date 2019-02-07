from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print('GET {0}'.format(self.path))
        self.send_response(200)
        self.send_header(b'Content-type', b'text/html')
        self.end_headers()
        self.wfile.write(b"Hello World !")
        return

    def do_POST(self):
        print('POST {0}'.format(self.path))
        payload = self.rfile.read(int(self.headers['content-length'])).decode('utf-8')
        print('Content-Type: {0}'.format(self.headers['content-type']))
        print(payload)

        self.send_response(200)
        self.send_header(b'Content-type', b'text/html')
        self.end_headers()
        self.wfile.write(b"All good!")
        return


server = HTTPServer(('', 8090), RequestHandler)
server.serve_forever()

