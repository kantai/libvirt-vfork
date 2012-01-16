import httplib
import sys
import time

def poke_it(ip,k):
    conn = httplib.HTTPConnection(ip)
    conn.request("GET", "/A?n=%s"%k)
    r1 = conn.getresponse()
    return r1.read()

def sequential_pokes(ip, number_of_pokes):
    times = []
    for k in range(3,4):
        for x in range(0, number_of_pokes):
            t0 = time.time() * 1000
            poke_it(ip,k)
            t1 = time.time() * 1000
            times.append((k, t1-t0))
    return times
    
if __name__ == "__main__":
    ip = sys.argv[1]
    num = int(sys.argv[2])
    times = sequential_pokes(ip,num)
    for t in times:
        print "%s %s" % t
