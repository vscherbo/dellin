#!/bin/sh

. /usr/local/bin/bashlib

cd "$(dirname "$0")"
LOG=$(namename "$0").log                                                          
exec 1>"$LOG" 2>&1

last_ca=$(
psql -At -U arc_energo <<EOT
SELECT ca_id FROM ext.dl_addresses a WHERE a.status <> 0                          
EOT
)

for ca in $last_ca
do
    logmsg INFO 'Ask addresses for ca='"$ca"
    ./get-address.sh "$ca"
    sleep 2
done

find . -type f -mtime +10 \( -name 'load-ca-*-addr.sql' -o -name 'ca_*_addr.csv' -o -name 'get-address-*.log' \) -delete
