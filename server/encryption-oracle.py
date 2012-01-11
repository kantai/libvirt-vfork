import fork
import hashlib
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint
import sys

class CryptoOracle(LineReceiver):
    def lineReceived(self, line):
        print "Crypto-oracle received message..."
        h = hashlib.sha256()
        h.update(line)
        self.sendLine(h.hexdigest())
class CryptoOracleFactory(Factory):
    def buildProtocol(self, addr):
        return CryptoOracle()

class CryptoClient(LineReceiver):
    def sendMessage(self, message, callback):
        self.callback = callback
        self.sendLine(message)
    def lineReceived(self, line):
        if self.callback:
            self.callback(self, line)

class CryptoClientFactory(Factory):
    def buildProtocol(self, addr):
        return CryptoClient()

def startup_crypto_oracle(ipaddr,port):
    reactor.listenTCP(port, CryptoOracleFactory())
    print "Starting crypto-oracle..."
    reactor.run()

def interaction_continue(crypto_client, response):
    print "SERVER: %s" % response
    line = sys.stdin.readline()
    crypto_client.sendMessage(line, interaction_continue)

def interaction_start(crypto_client):
    interaction_continue(crypto_client,
                         "Connected to oracle, submit you're queries!")

def do_interactive(oracle_ip, port):
    point = TCP4ClientEndpoint(reactor, oracle_ip, port)
    d = point.connect(CryptoClientFactory())
    d.addCallback(interaction_start)
    reactor.run()

def set_us_up_the_bomb():
    result,ipaddr = fork.do_fork()
    if result.startswith('parent'):
        do_interactive(ipaddr,port=8500)
    else:
        startup_crypto_oracle(ipaddr,port=8500)

if __name__ == "__main__":
    set_us_up_the_bomb()

