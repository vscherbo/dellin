#!/bin/sh

last_ca=$(
psql -At -U arc_energo <<EOT
SELECT ca_id FROM ext.dl_addresses a WHERE a.status <> 0                          
EOT
)

for ca in $last_ca
do
    echo 'Ask addresses for ca='"$ca"
    ./get-address.sh "$ca"
    sleep 2
done

find . -type f -mtime +10 \( -name 'load-ca-*-addr.sql' -o -name 'ca_*_addr.csv' -o -name 'get-address-*.log' \) -delete
