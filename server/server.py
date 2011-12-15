import libvirt
import shutil
from xml.dom.minidom import parseString

def do_fork():
    pass

def serve_loop():
    conn = libvirt.open(None)
    f = open("/dev/pts/1", "r+")
    while True:
        command = f.readline().strip()
        if command.startswith('fork'):
            broken = command.split()
            domain = broken[1]            
            dom = conn.lookupByName(domain)
            defn = parseString(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
            filename = defn.getElementsByTagName("disk")[0].getElementsByTagName(
                "source")[0].getAttribute('file')
            uuid = dom.UUID()
            nuu = uuid[:-1] + '\x01'
            print "forking %s" % domain
            dom.liveSave("/tmp/vm1-1", nuu, domain + ".1")
            print "copying..."
            subprocess.call(['qemu-img','create','-f', 'qcow2', '-b',filename,'/tmp/disk-foo.qcow2'])
            print "restoring..."
            conn.restore("/tmp/vm1-1")
            print "scribbling..."
            f.write("parent-forked\n")
            f.flush()
            child = conn.lookupByUUID(nuu)
            defn = parseString(child.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
            tty = defn.getElementsByTagName("serial")[0].getElementsByTagName(
                "source")[0].getAttribute("path")
            childfd = open(tty, "r+")
            childfd.write("child-forked\n")
            childfd.close()
            
serve_loop()
