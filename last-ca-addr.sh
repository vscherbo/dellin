#!/bin/sh

last_ca=$(
psql -At -U arc_energo <<EOT
SELECT ca.id FROM shp.vw_dl_counteragents ca WHERE ca."lastUpdate" > '2018-11-01 08:10:05.000'
EOT
)

for ca in $last_ca
do
    echo 'Ask addresses for ca='"$ca"
    ./get-address.sh "$ca"
    sleep 2
done

find . -type f -mtime +10 \( -name 'load-ca-*-addr.sql' -o -name 'ca_*_addr.csv' -o -name 'get-address-*.log' \) -delete
