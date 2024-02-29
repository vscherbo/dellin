#!/bin/bash

. /usr/local/bin/bashlib

if [ "$HOSTNAME" == "scherbova" ]
then
    PG_SRV=vm-pg.arc.world
else
    WRKDIR=/opt/dellin
    PG_SRV=localhost
    cd $WRKDIR
    
fi

LOG=$(namename "$0").log

exec 3>&1 1>>"$LOG" 2>&1

ca_total=$(
psql -h $PG_SRV -At -U arc_energo <<EOT
SELECT count(1) FROM ext.dl_counteragents
EOT
)
echo 'ca_total='$ca_total

############ DEBUG ca_total=100

rm -f res-ca-v2.txt

limit=200

iter=0
off=0
while [ $off -lt $ca_total ]
do
    echo 'off='$off

ca_list=$(
psql -h $PG_SRV -At -v limit=$limit -v offset=$off -U arc_energo <<EOT
SELECT array_to_string(ARRAY(SELECT id FROM ext.dl_counteragents LIMIT $limit OFFSET $off), ' ' )
EOT
)

logmsg INFO 'Req info for ca_list='"$ca_list"

# Обновить справочник контрагентов
#    на выходе файл res-counteragents.txt или res-counteragents-v2.txt
./get-dl-ca-full.py --log_level=INFO --ca_ids $ca_list
rc=$?
logmsg "$rc" "Загрузка с сайта Деллин завершена"
# check ret_code , output res-counteragents.txt



    iter=$((iter+1))
    off=$((limit*iter))
    echo 'iter='$iter', offset='$off
    sleep 4
done

if [ 0 -eq 1 ]
#if [ $rc -eq 0 ]
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
