/*
create type shp.dl_counteragent as (
"lastUpdate" timestamp,
name text,
form text,
type text,
inn text
);*/

drop view shp.vw_dl_counteragents;
create view shp.vw_dl_counteragents as
select *,
document->'type' as dl_doc_type,
document->'serial' as dl_doc_serial,
document->'number' as dl_doc_number,
document->'date'  as dl_doc_date
from 
(select (jsonb_populate_record(null::shp.dl_counteragent, jsonb_array_elements(values)->'counteragent')).* from shp.dl_counteragents_json) cnta
-- select (jsonb_populate_record(null::shp.dl_counteragent, jsonb_array_elements(values)->'counteragent')).* from shp.dl_counteragents_json
