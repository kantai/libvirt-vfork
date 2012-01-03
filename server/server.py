import libvirt
import shutil
import subprocess
from xml.dom.minidom import parseString
import os

conn = libvirt.open(None)

class DomainReader(object):
    def __init__(self, tty_fname, domain_name):
        self.tty_fname = tty_fname
        self.fd = os.open(tty_fname, os.O_RDWR)
        self.file = os.fdopen(self.fd, "r+")
        self.dom = domain_name
        self.children_counter = 0
        from twisted.internet import reactor
        reactor.addReader(self)
    def write_to(self, message):
        self.file.write(message)
        self.file.flush()
    def fileno(self):
        return self.fd
    def connectionLost(self, reason):
        pass
    def doRead(self):
        print "doRead called on %s" % self.tty_fname
        cmd = self.file.readline().strip()
        print cmd
        if cmd.startswith('fork'):
            self.children_counter += 1
            do_fork(self, cmd, self.children_counter)
    def logPrefix(self):
        return "reader"

def do_fork(parent_reader, str_command, child_count):
    broken = str_command.split()
    domain = broken[1]            
    dom = conn.lookupByName(domain)
    defn = parseString(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
    disk_from_filename = defn.getElementsByTagName("disk")[0].getElementsByTagName(
        "source")[0].getAttribute('file')
    uuid = dom.UUID()
    nuu = uuid[:-1] + chr(child_count)

    print "forking %s" % domain
    child_domname = "%s.%s" % (domain, child_count)

    livesave_filename = "/tmp/vm-%s" % child_domname
    disk_to_filename = "/tmp/disk-%s" % child_domname

    dom.liveSave(livesave_filename, nuu, child_domname, disk_to_filename)
    print "copying..."
    subprocess.call(['qemu-img','create','-f', 'qcow2', '-b',disk_from_filename,disk_to_filename])
    print "restoring..."
    conn.restore(livesave_filename)
    print "scribbling..."

    parent_reader.write_to("parent-forked\n")

    child = conn.lookupByUUID(nuu)
    defn = parseString(child.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
    tty_filename = defn.getElementsByTagName("serial")[0].getElementsByTagName(
        "source")[0].getAttribute("path")
    
    child_reader = DomainReader(tty_filename, child_domname)
    child_reader.write_to("child-forked\n")

def main():
    # add all the currently open domain readers!
    domainIDs = conn.listDomainsID()
    for domid in domainIDs:
        dom = conn.lookupByID(domid)
        defn = parseString(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
        tty_filename = defn.getElementsByTagName("serial")[0].getElementsByTagName(
            "source")[0].getAttribute("path")
        dom_name = dom.name()
        DomainReader(tty_filename, dom_name)
    from twisted.internet import reactor
    reactor.run()

main()
