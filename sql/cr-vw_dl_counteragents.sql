/*
create type dl_counteragent as (
"lastUpdate" timestamp,
name text,
form text,
type text,
inn text
);*/

create view vw_dl_counteragents as
select (jsonb_populate_record(null::dl_counteragent, jsonb_array_elements(values)->'counteragent')).* from dl_counteragents_json
