import subprocess

mac = "0c:22:d0:b8:78:af"

subprocess.call(["sudo", "ifdown", "eth0"])
subprocess.call(["sudo", "ifconfig", "eth0", "hw", "ether", mac])
subprocess.call(["sudo", "ifup", "eth0"])
subprocess.call(["sudo", "dhclient"])
