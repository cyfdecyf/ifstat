#!/usr/bin/env python

"""
A simple server for collecting interface statistics.
"""

from datetime import datetime
import logging
import os
from os import path
import sys

try:
    import socketserver
except:
    import SocketServer as socketserver

# Set interfaces we want to collect here.
INTERFACES = ['eth0', 'eth1', 'eth3', 'wg0']
# Local address to listen.
#LISTEN = '192.168.11.254'
LISTEN = '0.0.0.0'
PORT = 19998

LOG_FILE = '/var/log/ifstat.log'

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Change to this dir to avoid using full path to construct rx_bytes/packets/etc
# file path.
os.chdir('/sys/class/net')

class IfStat(object):
    def __init__(self,
            interfaces, stats=None):
        """
        interfaces: list of interfaces to collect statistics.
        stats: list of files to collect under /sys/class/net/ethX/statistics
        """
        # HEADER, '\r', '' are for building up a list that can be joined
        # directly to produce final output.
        self.interfaces = ['H'] + interfaces + ['E']
        self.stats = stats
        if self.stats is None:
            self.stats = [
                'rx_bytes', 'rx_packets', 'rx_dropped', 'rx_errors',
                'tx_bytes', 'tx_packets', 'tx_dropped', 'tx_errors'
            ]
        # HACK: for collecting interface name.
        self.stats.insert(0, 'itf')
        self.header = ','.join(self.stats)

    def collect(self):
        """Return a csv string with header line."""
        # To support multiple request and reply for a single socket, We use
        # '\r\n' to mean end of response.
        # For performance reason, the collect method returns data containing
        # '\r\n' so it can be directly sent as response.
        return '\n'.join((self.collect_one(i) for i in self.interfaces))

    @staticmethod
    def read_file(interface, stat):
        if stat == 'itf':
            return interface

        with open(path.join(interface, 'statistics', stat), 'r') as f:
            # Strip ending \n
            return f.read()[:-1]

    def collect_one(self, interface):
        if interface == 'H':
            return self.header
        elif interface == 'E':
            return '\r\n'

        return ','.join((self.read_file(interface, st) for st in self.stats))


class IfStatHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.ifstat = IfStat(INTERFACES)

    def handle(self):
        while True:
            try:
                data = self.request.recv(4)
                if data[:4] == b'data':
                    self.req_data()
                else:
                    # Seems client closing connection may lead to here.
                    raise RuntimeError('unknown request: {}'.format(data))
            except Exception as ex:
                logging.error("get exception {}".format(str(ex)))
                return

    def req_data(self):
        resp = self.ifstat.collect()
        #logging.debug('data resp:\n{}'.format(resp[:-2]))
        self.request.send(resp)


class IfStatServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    damon_threads = False
    allow_reuse_address = True

    def __init__(self, host, port):
        socketserver.TCPServer.__init__(self, (host, port), IfStatHandler)
        logging.info('starting IfStat server')


if __name__ == '__main__':
    server = IfStatServer(LISTEN, PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.error("Ctrl-C hit, exit")
        sys.exit(0)

