import httplib
import sys
import cProfile

def poke_it(ip):
    conn = httplib.HTTPConnection(ip)
    conn.request("GET", "/A")
    r1 = conn.getresponse()
    return r1.read()

def sequential_pokes(ip, number_of_pokes):
    for x in range(0, number_of_pokes):
        poke_it(ip)
    
if __name__ == "__main__":
    ip = sys.argv[1]
    num = int(sys.argv[2])
    sequential_pokes(ip,num)
#    cProfile.run("sequential_pokes(%s,%s)" % (ip, num))
