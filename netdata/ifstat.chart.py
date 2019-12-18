from bases.FrameworkServices.UrlService import UrlService

ORDER = [
    'Bandwidth',
    'Packets',
    'Drops',
    'Errors',
]

# For meaning of options and lines, refer to
# https://docs.netdata.cloud/collectors/plugins.d/#chart
# CHART type.id name title units family context charttype

CHARTS = {
    'Bandwidth': {
        'options': [None, 'Bandwidth', 'kilobits/s', 'eth0', 'ifstat.bandwidth', 'area'],
        'lines': [
            ['eth0_rx_bytes', 'received', 'incremental', 8, 1000],
            ['eth0_tx_bytes', 'sent', 'incremental', -8, 1000],
        ]
    },
    'Packets': {
        'options': [None, 'Packets', 'packets/s', 'eth0', 'ifstat.packets', 'line'],
        'lines': [
            ['eth0_rx_packets', 'received', 'incremental', 1, 1],
            ['eth0_tx_packets', 'sent', 'incremental', -1, 1],
        ]
    },
    'Drops': {
        'options': [None, 'Drops', 'drops/s', 'eth0', 'ifstat.drops', 'line'],
        'lines': [
            ['eth0_rx_dropped', 'inbound', 'incremental', 1, 1],
            ['eth0_tx_dropped', 'outbound', 'incremental', -1, 1],
        ]
    },
    'Errors': {
        'options': [None, 'Errors', 'errors', 'eth0', 'ifstat.errors', 'line'],
        'lines': [
            ['eth0_rx_errors', 'receive', 'incremental', 1, 1],
            ['eth0_tx_errors', 'transmit', 'incremental', -1, 1],
        ]
    },
}

class Service(UrlService):
    def __init__(self, configuration=None, name=None):
        UrlService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS

    def _get_data(self):
        self.debug("doing http request to '{0}'".format(self.url))
        raw = self._get_raw_data(self.url)
        self.debug("{0}'".format(raw))
        if not raw:
            return None

        lines = raw.splitlines()
        colname = lines[0].split(',')
        data = {}
        for l in lines[1:]:
            l = l.strip()
            if l == '':
                continue
            # interface
            cols = l.split(',')
            ifs = cols[0]
            if ifs != 'eth0':
                self.debug("skip {0}'".format(ifs))
                continue
            data.update(zip(
                ('{}_{}'.format(ifs, c) for c in colname[1:]), cols[1:]))
            self.debug("data {0}'".format(data))

        return data

