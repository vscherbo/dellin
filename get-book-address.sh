#!/bin/sh

. /usr/local/bin/bashlib

[ +$1 == + ] && { echo 1st parameter addr_id is required. Exit; exit 123; }
# TODO
# check $1 for digits

LOG=`namename $0`-${1}.log

./get-book-address.py --addr_id $1 --log_level=INFO --log_to_file=$LOG

SQL=sql/load-book-addr-${1}.sql.template
sed "s/:csv/addr_${1}.csv/" sql/load-book-addr.sql.template > $SQL
psql -a -U arc_energo -v ADDR_ID=$1 -f $SQL >> $LOG 2>&1

# rm -f $SQL
# OR find ./sql -type f -mtime +10 -name load-ca-*-addr.sql -delete
