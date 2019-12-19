#!/bin/bash

# Check version before we make any modifications.
# To avoid breaking the system in case a new version of EdgeOS uses something
# different for ssl config.

edgeos_version=$(/opt/vyatta/bin/vyatta-op-cmd-wrapper show version | awk '/Version:/ { print $2 }')

if [[ "$edgeos_version" != "v1.10.10" ]]; then
    echo "ERROR: edgeos version NOT supported for disabling https redirect"
    exit 0
fi

#mv -f /etc/lighttpd/conf-enabled/10-ssl.conf /etc/lighttpd/conf-enabled/10-ssl.conf.bak
#cp -f /config/scripts/10-ssl.conf /etc/lighttpd/conf-enabled/10-ssl.conf

# Remove http redirect related config.
sed -i.bak -e '/$HTTP\["scheme"\] == "http" {/,/^}/ d' /etc/lighttpd/conf-enabled/10-ssl.conf

