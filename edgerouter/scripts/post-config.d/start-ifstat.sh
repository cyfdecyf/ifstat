#!/bin/bash

ln -sfn /tmp/ifstat.txt /var/www/htdocs/media/

# MUST run as background process to avoid blocking router startup.
nohup /config/scripts/ifstat.sh >/dev/null 2>&1 &

