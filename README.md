# The wrong approach (separating data generation and collection)

The approach I first used turns out to be wrong. In this approach:

- Router device generates data in a while loop, sleeping a little less than 1
  second between every data generations
- Netdata plugin collects data every 1 second

The key problem here is that the generated data does not align with netdata
collection interval. This may lead to wrong statistics values. 
Consider following scenario (suppose time starts at 0 second):

1. data generated on 0.01 second
2. netdata collects data at 1.00 second
3. data generated on 1.01 second
4. netdata collects data at 2.02 second

In this case, netdata collects value which represents a 2 seconds interval
instead of 1 second. Thus we could see wrong spikes in chart.

The proper way to do this is written in
[document](https://docs.netdata.cloud/collectors/plugins.d/#writing-plugins-properly).
The core idea is to collect data at exactly constant rate.

So it's better to let netdata plugin collection trigger data generation. That's
why we moved to use SNMP for moniting EdgeRouter interfaces. As snmpd manual
says, it collects data upon receiving request.

## Usage (for the wrong approach)

This mainly serves as an example to write netdata plugin because of problems
described above.

1. Run `ifstat.sh` on Linux system which we want to get interface statistics
2. Deploy netdata plugin and config to a running netdata server
   1. Copy `netdata/ifstat.chart.py` to netdata `plugins.d/python.d.plugin` directory
   2. Edit `netdata/ifstat.conf` and then copy to `etc/netdata/python.d` directory
