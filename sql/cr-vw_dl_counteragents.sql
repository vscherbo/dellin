-- drop view shp.vw_dl_counteragents;

-- recreate type
drop type shp.dl_counteragent cascade;
create type shp.dl_counteragent as (
"id" integer,
"uid" UUID,
"lastUpdate" timestamp,
"name" varchar,
"form" varchar,
"type" varchar,
"inn" varchar,
"addresses" integer,
"Email" varchar,
"Phone" varchar,
"document" json
);

create view shp.vw_dl_counteragents as
select *,
document->'type' as dl_doc_type,
document->'serial' as dl_doc_serial,
document->'number' as dl_doc_number,
document->'date'  as dl_doc_date
from 
(select (jsonb_populate_record(null::shp.dl_counteragent, jsonb_array_elements(values)->'counteragent')).* from ext.dl_counteragents_json) cnta;

\i cr-vw_dl_addr_contact_ext.sql
\i cr-vw_dl_addr_phone_ext.sql
