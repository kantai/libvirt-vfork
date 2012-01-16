import fork
import httplib
import cherrypy

myN = 0

ipNext = None

class Cherry(object):
    def A(self,n=None):
        if n is None or myN == int(n):
            return "You reached page %s!" % n
        return send_request(ipNext, "/A?n=%s"%n)
    A.exposed = True

def send_request(ip, path):
    conn = httplib.HTTPConnection(ip)
    conn.request("GET", path)
    r1 = conn.getresponse()
    return r1.read()

def do_server():
    print "Setting up httpd for %s " % myN
    s = Cherry()
    
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = 80
    cherrypy.quickstart(s)

def do_fork_again():
    global myN, ipNext
    (resp, ip_addr) = fork.do_fork()
    if resp.startswith("child"):
        myN += 1
        if myN == 9:
            return do_server()
        return do_fork_again()
    else:
        ipNext = ip_addr
        do_server()

def do_set_us_up_the_bomb():
    do_fork_again()

if __name__ == "__main__":
    do_set_us_up_the_bomb()
