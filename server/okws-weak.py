import httplib
import subprocess
import cherrypy
import sys

existential_purpose = None

sockA = '/tmp/a.sock'
sockB = '/tmp/b.sock'

def send_request(port, path):
    conn = httplib.HTTPConnection("fake.com")
    conn.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn.sock.connect(port)
    conn.request("GET", path)
    r1 = conn.getresponse()
    return r1.read()

class CherryRouter(object):
    def A(self):
        return "You reached page A!"
    def B(self):
        return "You reached page A!"
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

def do_server():
    print "Setting up httpd for %s " % existential_purpose
    if existential_purpose == "TO_ROUTE":
        s = CherryRouter()
    elif existential_purpose == "TO_OUTPUT_A":
        s = CherryA()
        cherrypy.server.socket_file = sockA
    elif existential_purpose == "TO_OUTPUT_B":
        s = CherryB()
        cherrypy.server.socket_file = sockB
#    cherrypy.server.socket_host = "localhost"
    cherrypy.quickstart(s)

if __name__ == "__main__":
    p = int(sys.argv[1])
    if p == 0:
        existential_purpose = "TO_ROUTE"
    elif p == 1:
        existential_purpose = "TO_OUTPUT_A"
    elif p == 2:
        existential_purpose = "TO_OUTPUT_B"
    do_server()
