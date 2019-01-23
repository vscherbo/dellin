#!/bin/sh

last_a=$(
psql -At -U arc_energo <<EOT
SELECT id FROM ext.dl_addr_contact WHERE status <> 0
UNION
SELECT id FROM ext.dl_addr_phone WHERE status <> 0
EOT
)
# AND ( contacts <> 0 OR phones <> 0 )

for a in $last_a
do
    echo 'Ask contacts for addr='"$a"
    ./get-book-address.sh "$a"
    sleep 2
done

find . -type f -mtime +10 \( -name 'load-book-addr-*.sql' -o -name 'addr_*.csv' -o -name 'get-book-address-*.log' \) -delete

