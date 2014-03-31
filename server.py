"""
Basic DNS server that will ask the user to answer manually all queries.
Based on code by Jochen Ritzel (see http://stackoverflow.com/a/4401671)
"""

from twisted.names import dns, server, client, cache
from twisted.internet import reactor
import socket

class ManualResolver(client.Resolver):
    """
    Resolves names by asking the user.
    """

    def __init__(self, servers):
        client.Resolver.__init__(self, servers=servers)
        self.ttl = 10 # XXX

    def lookupAddress(self, name, timeout=None):
        print "A-record requested for {!r}.".format(name)

        response = None
        while response is None:
            response = raw_input("What IP address shall we respond with? ")
            try:
                # Use inet_aton to check input validity instead of doing it
                # ourselves
                socket.inet_aton(response)
            except socket.error:
                print "Sorry, please enter a valid IP address."
                response = None

        result = [(dns.RRHeader(name, dns.A, dns.IN, self.ttl, dns.Record_A(response, self.ttl)),),
                  (), ()] # put it in a A Record

        return result

        # TODO: allow deferal? see below
        #return self._lookup(name, dns.IN, dns.A, timeout)

class TalkativeDNSServerFactory(server.DNSServerFactory):
    def __init__(self, *args, **kwargs):
        server.DNSServerFactory.__init__(self, *args, **kwargs)

    def handleQuery(self, message, protocol, address):
        print 
        print "Received query from {}:".format(address[0])
        return server.DNSServerFactory.handleQuery(self, message, protocol, address)

    def sendReply(self, protocol, message, address):
        server.DNSServerFactory.sendReply(self, protocol, message, address)
        print "Reply sent!"


if __name__ == '__main__':
    print "=== Manual DNS Server Started ==="
    print "Waiting for requests..."

    # set up a resolver that uses user input or a secondary nameserver
    manual_resolver = ManualResolver(servers=[('8.8.8.8', 53)])

    # create the protocols
    #f = TalkativeDNSServerFactory(caches=[cache.CacheResolver()], clients=[manual_resolver])
    f = TalkativeDNSServerFactory(clients=[manual_resolver])
    p = dns.DNSDatagramProtocol(f)
    f.noisy = p.noisy = False

    reactor.listenUDP(53, p)
    reactor.run()
