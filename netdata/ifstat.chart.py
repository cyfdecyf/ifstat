from datetime import datetime

from bases.FrameworkServices.SocketService import SocketService

class Service(SocketService):
    def __init__(self, configuration=None, name=None):
        SocketService.__init__(self, configuration=configuration, name=name)
        self._keep_alive = True
        self.alias = configuration.get('alias')
        self.request = 'data'

    def create_charts(self, ifname):
        order = [
            f'{ifname}_bandwidth',
            f'{ifname}_packets',
            f'{ifname}_drops',
            f'{ifname}_errors',
        ]
        if self.alias and ifname in self.alias:
            family = f'{ifname} ({self.alias[ifname]})'
        else:
            family = ifname

        # For meaning of options and lines, refer to
        # https://docs.netdata.cloud/collectors/plugins.d/#chart
        # CHART type.id name title units family context charttype
        charts = {
            order[0]: {
                'options': [None, 'Bandwidth', 'kilobits/s', family, 'ifstat.bandwidth', 'area'],
                'lines': [
                    [f'{ifname}_rx_bytes', 'received', 'incremental', 8, 1000],
                    [f'{ifname}_tx_bytes', 'sent', 'incremental', -8, 1000],
                ]
            },
            order[1]: {
                'options': [None, 'Packets', 'packets/s', family, 'ifstat.packets', 'line'],
                'lines': [
                    [f'{ifname}_rx_packets', 'received', 'incremental', 1, 1],
                    [f'{ifname}_tx_packets', 'sent', 'incremental', -1, 1],
                ]
            },
            order[2]: {
                'options': [None, 'Drops', 'drops/s', family, 'ifstat.drops', 'line'],
                'lines': [
                    [f'{ifname}_rx_dropped', 'inbound', 'incremental', 1, 1],
                    [f'{ifname}_tx_dropped', 'outbound', 'incremental', -1, 1],
                ]
            },
            order[3]: {
                'options': [None, 'Errors', 'errors', family, 'ifstat.errors', 'line'],
                'lines': [
                    [f'{ifname}_rx_errors', 'receive', 'incremental', 1, 1],
                    [f'{ifname}_tx_errors', 'transmit', 'incremental', -1, 1],
                ]
            },
        }

        return order, charts


    def check(self):
        # Call parent class check first, so we can use _get_raw_data in check.
        if not SocketService.check(self):
            return False

        raw = self._get_raw_data()

        interfaces = [ l.split(',')[0] for l in raw.splitlines()[1:] if l.strip() != '' ]

        self.debug('available interfaces {}'.format(interfaces))
        self.order = []
        self.definitions = {}
        for i in interfaces:
            order, charts = self.create_charts(i)
            self.order.extend(order)
            self.definitions.update(charts)

        return True

    @staticmethod
    def _check_raw_data(data):
        return len(data) >= 2 and data[-2:] == '\r\n'


    def _get_data(self):
        raw = self._get_raw_data()
        self.debug("response on {1}\n{0}".format(raw, datetime.now()))
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
            data.update(zip(
                ('{}_{}'.format(ifs, c) for c in colname[1:]),
                cols[1:]))
        self.debug('data {0}'.format(data))

        return data

