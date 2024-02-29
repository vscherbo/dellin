#!/bin/bash

. /usr/local/bin/bashlib

WRKDIR=/opt/dellin
cd $WRKDIR
LOG=$(namename "$0").log

exec 3>&1 1>>"$LOG" 2>&1

last_ca=$(
psql -At -U arc_energo <<EOT
SELECT id FROM ext.dl_counteragents a WHERE a.status <> 0
LIMIT 1;
EOT
)

for ca in $last_ca
do
    logmsg INFO 'Req info for ca='"$ca"
    # Обновить справочник контрагентов
    #    на выходе файл res-counteragents.txt или res-counteragents-v2.txt
    ./get-dl-ca.py --log_level=INFO --ca_id="$ca"
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

    sleep 2
done

exec 1>&3

egrep -v -f "${LOG}"-template "$LOG" | mail -E -s "$LOG events" it@kipspb.ru

exit $rc
