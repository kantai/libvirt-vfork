import os
import subprocess

def change_mac(mac):
    subprocess.call(["sudo", "ifdown", "eth0"])
    subprocess.call(["sudo", "ifconfig", "eth0", "hw", "ether", mac])
    subprocess.call(["sudo", "ifup", "eth0"])
    subprocess.call(["sudo", "dhclient"])

get_ip_cmd = """ifconfig eth0 | grep inet | grep -v inet6 | cut -d ":" -f 2 | cut -d " " -f 1"""
def get_ip():
    ip = subprocess.check_output(["bash","-c",get_ip_cmd]).strip()
    return ip

def do_fork():
    fd = os.open("/dev/ttyS0", os.O_RDWR)
    file = os.fdopen(fd, "r+")
    file.write("fork\n")
    file.flush()
    ret = file.readline().strip()
    if ret.startswith('child'):
        vals = ret.split(" ")
        mac = vals[1]
        change_mac(mac)
        ip = get_ip()
        file.write("notify-ip %s\n" % ip) 
        file.flush()
        ret = (ret, ip)
    return ret

if __name__ == "__main__":
    print do_fork()
