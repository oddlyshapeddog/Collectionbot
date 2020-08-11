from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import ssl
import socketserver
from artbot_utilities import Config

config = Config()
config.live = False #Use this flag to change between live and test config
config.LoadFromFile('config.txt')

certpath = os.path.join(os.getcwd(), 'cert.pem')
keypath = os.path.join(os.getcwd(), 'key.pem')

os.chdir(os.path.join(os.getcwd(), 'frontend'))
cwd = os.getcwd()

class CustomRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/config":
            print("GET {0}".format(self.path))
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config.__dict__).encode())
        else:
            SimpleHTTPRequestHandler.do_GET(self)

def run(server_class=HTTPServer, handler_class=CustomRequestHandler, port=8000, directory=cwd):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.directory = directory
    httpd.socket = ssl.wrap_socket (
        httpd.socket, 
        keyfile=keypath, 
        certfile=certpath,
        server_side=True)
    print("serving {0} at https://localhost:{1}".format(directory, port))
    httpd.serve_forever()

print("starting a local web server...")
run()
