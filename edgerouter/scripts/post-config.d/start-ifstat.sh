#!/bin/bash

# MUST run as background process to avoid blocking router startup.
nohup /config/scripts/ifstat.py >/dev/null 2>&1 &

