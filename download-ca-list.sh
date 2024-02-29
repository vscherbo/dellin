#!/bin/bash

. /usr/local/bin/bashlib

WRKDIR=/opt/dellin
cd $WRKDIR
LOG=$(namename "$0").log

exec 3>&1 1>>"$LOG" 2>&1

ca_list=$(
psql -At -U arc_energo <<EOT
SELECT array_to_string(ARRAY(SELECT id FROM ext.dl_counteragents WHERE status <> 0 LIMIT 200), ' ' )
EOT
)

logmsg INFO 'Req info for ca_list='"$ca_list"
# Обновить справочник контрагентов
#    на выходе файл res-counteragents.txt или res-counteragents-v2.txt
./get-dl-ca-list.py --log_level=INFO --ca_ids $ca_list
rc=$?
logmsg "$rc" "Загрузка с сайта Деллин завершена"
# check ret_code , output res-counteragents.txt
if [ $rc -eq 0 ]
then
    # выполняем на PG, параметр -h vm-pg опускаем 
    # psql --echo-all --variable ON_ERROR_STOP=ON -U arc_energo -f sql/copy-dl-counteragents.sql
    # psql --echo-all --variable ON_ERROR_STOP=ON -U arc_energo -f sql/inc-dl-counteragents-v2.sql
    psql --variable ON_ERROR_STOP=ON -U arc_energo -f sql/inc-dl-counteragents-v2.sql
    rc=$?
    logmsg "$rc" "Загрузка в PG завершена"
fi

exec 1>&3

egrep -v -f "${LOG}"-template "$LOG" | mail -E -s "$LOG events" it@kipspb.ru

exit $rc
