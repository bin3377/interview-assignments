#!/usr/bin/python

import http.server
import socketserver
import json

PORT = 8000

class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        print("======= GET STARTED =======")
        print(self.headers)
        print("===========================")
    def do_POST(self):
        print("======= POST STARTED ======")
        print(self.headers)
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()
        data = json.loads(self.data_string)
        print(len(data), "entries received")
        print("===========================")
Handler = ServerHandler

httpd = socketserver.TCPServer(("", PORT), ServerHandler)

httpd.serve_forever()