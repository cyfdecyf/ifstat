#!/bin/bash

# Collect and combine interface statistics (rx/tx bytes & packets).

dstfile=/tmp/ifstat.txt

cd /sys/class/net

# Manually specify interfaces we want to monitor.
# This avoids unnecessary cost on weak CPU devices, also avoids showing charts
# we are not interested with.
ifs=(eth0 eth1 eth3 wg0)

while true; do
    cont="ifs,rx_bytes,rx_packets,rx_dropped,rx_errors,tx_bytes,tx_packets,tx_dropped,tx_errors"
    for i in "${ifs[@]}"; do
        cd $i/statistics
        cont+="\n$i,$(<rx_bytes),$(<rx_packets),$(<rx_dropped),$(<rx_errors),$(<tx_bytes),$(<tx_packets),$(<tx_dropped),$(<tx_errors)"
        cd ../..
    done
    echo -e $cont > $dstfile.tmp
    mv -f $dstfile.tmp $dstfile
    # Sleep a little less than 1 second, so fetcher with 1 second frequency will
    # not get stale data if the above collecting tasks finish fast enough.
    sleep 0.98
done

