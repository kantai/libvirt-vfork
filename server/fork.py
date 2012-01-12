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
    subprocess.call(['bash','-c','echo "fork" > /dev/ttyS0'])
    ret = subprocess.check_output(['head', '-n', '1', '/dev/ttyS0']).strip()
    if ret.startswith('child'):
        vals = ret.split(" ")
        mac = vals[1]
        change_mac(mac)
        ip = get_ip()
        subprocess.call(['bash','-c','echo "notify-ip %s" > /dev/ttyS0' % ip])
        return (ret, ip)
    elif ret.startswith('parent'):
        return (ret, ret.split(" ")[1])
    return ret

if __name__ == "__main__":
    print do_fork()
