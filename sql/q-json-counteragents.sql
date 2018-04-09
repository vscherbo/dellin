/*
create type dl_counteragent as (
"lastUpdate" timestamp,
name text,
form text,
type text,
inn text
);*/


-- it's work select (jsonb_populate_recordset(null::dl_counteragents, values)).* from dl_counteragents_json
-- WORKS select jsonb_each_text(jsonb_array_elements(values)->'counteragent') from dl_counteragents_json

-- SUPER !!! 
-- drop view vw_dl_counteragents;
create view vw_dl_counteragents as
select (jsonb_populate_record(null::dl_counteragent, jsonb_array_elements(values)->'counteragent')).* from dl_counteragents_json
-- It's work select values->>'counteragent' as company from (select json_array_elements(values::json) as values from dl_counteragents_json) j
