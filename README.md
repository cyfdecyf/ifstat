# Usage

1. Run `ifstat.sh` on Linux system which we want to get interface statistics
2. Deploy netdata plugin and config to a running netdata server
   1. Copy `netdata/ifstat.chart.py` to netdata `plugins.d/python.d.plugin` directory
   2. Edit `netdata/ifstat.conf` and then copy to `etc/netdata/python.d` directory
