-- copy downloaded data into production table
TRUNCATE TABLE ext.dl_counteragents_json;
\copy ext.dl_counteragents_json FROM res-counteragents-v2.txt;

-- truncate 'daily' table
-- TRUNCATE TABLE ext.dl_counteragents;

-- insert fresh data into 'daily' table
INSERT INTO ext.dl_counteragents (
    SELECT DISTINCT id, uid, "lastUpdate", "name", form,
            CASE
                WHEN juridical THEN 'juridical'
                ELSE 'private'
                END AS "type",
                 inn, "Email", "Phone", addresses, dl_doc_type, dl_doc_serial, dl_doc_number, dl_doc_date
    FROM shp.vw_dl_counteragents_v2
) ON CONFLICT (id)
DO UPDATE SET
    uid = EXCLUDED.uid
,    "lastUpdate" = EXCLUDED."lastUpdate"
,    "name" = EXCLUDED."name"
,    form = EXCLUDED.form
,    inn = EXCLUDED.inn
,    "type" = EXCLUDED."type"
,    "Email" = EXCLUDED."Email"
,    "Phone" = EXCLUDED."Phone"
,    addresses = EXCLUDED.addresses
,    dl_doc_type = EXCLUDED.dl_doc_type
,    dl_doc_serial = EXCLUDED.dl_doc_serial
,    dl_doc_number = EXCLUDED.dl_doc_number
,    dl_doc_date = EXCLUDED.dl_doc_date
,    status = 0;


-- DO NOTHING;

/*** НЕ УДАЛЯТЬ пока заполняется справочник v2
delete from ext.dl_counteragents where id in (
select e.id from ext.dl_counteragents e
left join shp.vw_dl_counteragents_v2 v on e.id = v.id
where v.id is null);
**/

