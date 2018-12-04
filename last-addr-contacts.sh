#!/bin/sh

last_a=$(
psql -At -U arc_energo <<EOT
SELECT a.id FROM shp.vw_dl_addresses a WHERE a."lastUpdate" > '2018-11-01 08:10:05.000'
AND ( contacts <> 0 OR phones <> 0 )
EOT
)

for a in $last_a
do
    echo 'Ask contacts for addr='"$a"
    ./get-book-address.sh "$a"
    sleep 2
done

find . -type f -mtime +10 \( -name 'load-book-addr-*.sql' -o -name 'addr_*.csv' -o -name 'get-book-address-*.log' \) -delete

