#!/bin/bash

. /usr/local/bin/bashlib

[ "+$1" = "+" ] && { echo 1st parameter addr_id is required. Exit; exit 123; }
# TODO
# check $1 for digits

LOG=$(namename "$0")-${1}.log

./get-book-address.py --addr_id "$1" --log_level=INFO --log_to_file="$LOG"

OP_NAME=load-book-addr
SQL=sql/${OP_NAME}-${1}.sql
sed "s/:csv/addr_${1}.csv/" sql/${OP_NAME}.sql.template > "$SQL"
psql -a -U arc_energo -v ADDR_ID="$1" -f "$SQL" >> "$LOG" 2>&1

# rm -f $SQL
# OR find ./sql -type f -mtime +10 -name "${OP_NAME}-*.sql" -delete
find ./sql -type f -mtime +10 -name "${OP_NAME}-*.sql" -ls

# remove obsolete rotated logs
find . -type f -mtime +30 -name \"$(namename "$0")*log*.gz\" -ls -delete

