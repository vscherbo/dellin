#!/bin/sh

. /usr/local/bin/bashlib

LOG=`namename $0`.log
exec 1>$LOG 2>&1

[ +$1 == + ] && { logmsg ERROR '1st parameter - dellin url is required!'; exit 123; }

DICT_URL=$1
dict_file=`namename $DICT_URL`
dict_type=`ext $DICT_URL`
PG_SRV='vm-pg-devel.arc.world'

logmsg INFO "dict_file=$dict_file, dict_type=$dict_type"

#arc_hash=`
arc_db=`
psql -At -h $PG_SRV -U arc_energo <<EOT
select dl_dict_hash, shp_table from shp.dl_dict where dl_dict_url='$DICT_URL'
EOT
`

IFS='|' read -ra arc_data <<< "$arc_db"
arc_hash=${arc_data[0]}
arc_table=${arc_data[1]}
logmsg INFO "from DB: hash=${arc_hash}, table=${arc_table}"

# TODO check select result

#DL_RES=(`./get-any-directory.py --url=$DICT_URL --log_to_file get-dl-terminals.log --log_level INFO`)
DL_RES=(`./get-any-directory.py --url=$DICT_URL --log_level INFO`)

dl_hash=${DL_RES[0]}
file_url="${DL_RES[1]}"
DT=`date +%F_%H_%M_%S`
TMP_DOWNLOAD=dl_dict.tmp

if [ +$arc_hash == +$dl_hash ]
then
    logmsg INFO "hash is $dl_hash the same for $DICT_URL. Exiting" 
    exit 0
fi    

logmsg INFO "new hash $dl_hash found: download and update"
rc_copy=100
wget "$file_url" -O $TMP_DOWNLOAD
rc_wget=$?
logmsg $rc_wget "wget completed"
if [ $rc_wget -ne 0 ]
then
    logmsg WARNING "Download $file_url failed. Do not load to DB. Exiting"
    exit 124
fi

DEST=${dict_file}_${DT}${dict_type}
logmsg INFO "DEST=$DEST"
if [ +$dict_type == '+.json' ]
then
    logmsg INFO "do json $DEST"
    tr -d '\n' < $TMP_DOWNLOAD | sed -e 's/"/""/g' -e 's/^/"[/' -e 's/$/]"/' > $DEST
psql -At -h $PG_SRV -U arc_energo <<EOT
truncate table $arc_table;
\copy $arc_table from $DEST with(format csv);
EOT
    rc_copy=$?
elif [ +$dict_type == '+.csv' ]
then    
    logmsg INFO "do csv $DEST"
else
    logmsg WARNING "unknown dict type [${dict_type}]. Exiting"
    exit 125
fi
logmsg $rc_copy "copy to DB completed"
# if copied, update hash in dl_dict
if [ $rc_copy -eq 0 ]
then
psql -At -h $PG_SRV -U arc_energo <<EOT
update shp.dl_dict set dl_dict_hash='$dl_hash', dt_upd=now() where dl_dict_url='$DICT_URL';
EOT
fi

