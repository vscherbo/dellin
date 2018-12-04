#!/bin/sh

. /usr/local/bin/bashlib

[ +$1 == + ] && { echo 1st parameter ca_id is required. Exit; exit 123; }
# TODO
# check $1 for digits

LOG=`namename $0`-${1}.log

./get-address.py --ca_id $1 --log_level=INFO --log_to_file=$LOG

SQL=sql/load-ca-$1-addr.sql
sed "s/:csv/ca_${1}_addr.csv/" sql/load-ca-addr.sql.template > $SQL
psql -a -U arc_energo -v CA_ID=$1 -f $SQL >> $LOG 2>&1

# rm -f $SQL
# OR find ./sql -type f -mtime +10 -name load-ca-*-addr.sql -delete
