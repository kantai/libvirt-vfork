import os
import subprocess

def change_mac(mac):
    subprocess.call(["sudo", "ifdown", "eth0"])
    subprocess.call(["sudo", "ifconfig", "eth0", "hw", "ether", mac])
    subprocess.call(["sudo", "ifup", "eth0"])
    subprocess.call(["sudo", "dhclient"])


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
    return ret

if __name__ == "__main__":
    print do_fork()
