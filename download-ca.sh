#!/bin/bash

. /usr/local/bin/bashlib

WRKDIR=/opt/dellin
cd $WRKDIR
LOG=$(namename "$0").log

exec 1>"$LOG" 2>&1
# Обновить справочник контрагентов
#    на выходе файл res-counteragents.txt
./get-dl-ca.py --log_level=INFO
rc=$?
# check ret_code , output res-counteragents.txt
if [ $rc -eq 0 ]
then
    # выполняем на PG, параметр -h vm-pg опускаем 
    psql --echo-all --variable ON_ERROR_STOP=ON -U arc_energo -f sql/copy-dl-counteragents.sql
    rc=$?
fi

exit $rc
