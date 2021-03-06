import fork
import httplib
import subprocess
import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cherrypy

existential_purpose = None

ipA = None
ipB = None

def send_request(ip, path):
    conn = httplib.HTTPConnection(ip)
    conn.request("GET", path)
    r1 = conn.getresponse()
    return r1.read()

class CherryRouter(object):
    def A(self):
        return send_request(ipA, "/A")
    def B(self):
        return send_request(ipB, "/B")
    A.exposed = True
    B.exposed = True
class CherryA(object):
    def A(self):
        return "You reached page A!"
    A.exposed = True
class CherryB(object):
    def B(self):
        return "You reached page B!"
    B.exposed = True

class SillyHandler(BaseHTTPRequestHandler):
    def send_OK_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):
        if existential_purpose == "TO_ROUTE":
            if self.path.startswith("/a"):
                out = send_request(ipA, self.path)
            else:
                out = send_request(ipB, self.path)

            self.wfile.write(out)
            return
        elif existential_purpose == "TO_OUTPUT_A":
            self.send_OK_headers()
            self.wfile.write("<html><h1>You reached page A!</h1>")
            print self.path
            parsed_u = urlparse.urlparse(self.path)
            qs = urlparse.parse_qs(parsed_u.query)
            if 'cmd' in qs:
                out = subprocess.check_output(["bash", "-c", qs['cmd'][0]])
                self.wfile.write("<i>%s</i>" % out)
            self.wfile.write("</html>")
            return
        elif existential_purpose == "TO_OUTPUT_B":
            print self.path
            self.send_OK_headers()
            self.wfile.write("<html><h1>You reached page B!</h1></html>")
            return

def do_server():
    print "Setting up httpd for %s " % existential_purpose
    if existential_purpose == "TO_ROUTE":
        s = CherryRouter()
    elif existential_purpose == "TO_OUTPUT_A":
        s = CherryA()
    elif existential_purpose == "TO_OUTPUT_B":
        s = CherryB()
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = 80
    cherrypy.quickstart(s)

def do_set_us_up_the_bomb():
    global existential_purpose, ipA, ipB
    existential_purpose = "TO_ROUTE"
    (resp, ip_addr) = fork.do_fork()
    if resp.startswith("child"):
        existential_purpose = "TO_OUTPUT_A"
        do_server()
        return
    ipA = ip_addr
    (resp, ip_addr) = fork.do_fork()
    if resp.startswith("child"):
        existential_purpose = "TO_OUTPUT_B"
        do_server()
        return
    ipB = ip_addr
    do_server()

if __name__ == "__main__":
    do_set_us_up_the_bomb()

