# Interface Statistics

Use netdata to collect interfaces statistics on remote linux system.

I write this tool because I want one second granularity interface statistics on
EdgeRouter.

# Usage

1. Run `ifstat.py` on Linux system which we want to get interface statistics
   - Modify `INTERFACES`, 'LISTEN' and `PORT` according to your need
2. Deploy netdata plugin and config to a running netdata server
   1. Copy `netdata/ifstat.chart.py` to netdata `plugins.d/python.d.plugin` directory
   2. Edit `netdata/ifstat.conf` and then copy to `etc/netdata/python.d` directory

# How does it work

- `ifstat.py` starts a simple socket server on remote linux system
   - Upon receiving request, it reads various files under
   `/sys/class/net/<itf>/statistics/` and combines them into csv format and then
   send back
- `netdata/ifstat.chart.py` is a netdata plugin written in Python
  - It sends requests to the above socket server defined in
    `netdata/ifstat.conf`, parses response and then generates output for netdata

Because data collection is triggered by netdata, so always get data that's most
current. This is avoids getting data that's not aligned with collection
frequency. We can also stop collection simply by removing socket server in
config without touching on remote linux system.

## Overhead on remote Linux system

By watching output of top:

- For ER-X, collecting 4 interfaces takes less than 1.3% CPU usage
- For ER-12, collecting 8 interfaces takes 1% ~ 2% CPU usage

Memory (`RES`) used is less than 4800 bytes.

## Debugging netdata plugin

After deploying the python plugin, run following command:

```
bash plugins.d/python.d.plugin ifstat debug trace
```

If everything works fine, we will see lines starting with `BEGIN`, `SET`, etc.
that's for netdata.

# The wrong approach (separating data generation and collection)

The approach I first used turns out to be wrong. In this approach:

- Remote device generates data in a while loop, sleeping a little less than 1
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
why I moved to use Python socket server for moniting EdgeRouter interfaces.
Not using SNMP is because update latency for snmpd.

For reference, `obselect/ifstat.sh` is kept as an example of collecting data
separately.
