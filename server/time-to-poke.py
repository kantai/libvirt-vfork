import httplib
import sys
import time

def poke_it(ip):
    conn = httplib.HTTPConnection(ip)
    conn.request("GET", "/A")
    r1 = conn.getresponse()
    return r1.read()

def sequential_pokes(ip, number_of_pokes):
    times = []
    for x in range(0, number_of_pokes):
        t0 = time.time() * 1000
        poke_it(ip)
        t1 = time.time() * 1000
        times.append(t1-t0)
    return times
    
if __name__ == "__main__":
    ip = sys.argv[1]
    num = int(sys.argv[2])
    times = sequential_pokes(ip,num)
    for t in times:
        print t

#    cProfile.run("sequential_pokes(%s,%s)" % (ip, num))
