-- drop view shp.vw_dl_counteragents;

-- recreate type
/***
drop type shp.dl_counteragent cascade;
create type shp.dl_counteragent as (
"id" integer,
"uid" UUID,
"lastUpdate" timestamp,
"name" varchar,
"form" varchar,
"type" varchar,
"inn" varchar,
"document" json,
"Email" varchar,
"Phone" varchar,
"addresses" integer
);
**/

create or replace view shp.vw_z_dl_counteragents as
select *,
trim('"' from (document->'type')::varchar) as dl_doc_type,
trim('"' from (document->'serial')::varchar)  as dl_doc_serial,
trim('"' from (document->'number')::varchar)  as dl_doc_number,
trim('"' from (document->'date')::varchar)   as dl_doc_date
from 
(select (jsonb_populate_record(null::shp.dl_counteragent, jsonb_array_elements(values)->'counteragent')).* from ext.z_dl_counteragents_json) cnta;

-- \i cr-vw_dl_addr_contact_ext.sql
-- \i cr-vw_dl_addr_phone_ext.sql
