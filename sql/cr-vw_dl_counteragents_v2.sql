-- drop view shp.vw_dl_counteragents;

-- recreate type
DROP TYPE shp.dl_counteragent_v2 cascade;
CREATE TYPE shp.dl_counteragent_v2 AS (
    id int4,
    uid varchar,
    form varchar,
    formUID varchar,
    "name" varchar,
    "Email" varchar,
    "Phone" varchar,
    juridical bool,
    inn varchar,
    addresses integer,
    "document" json,
    "lastUpdate" timestamp,
    "countryUid" varchar,
    "dataForReceipt" json);          

CREATE VIEW shp.vw_dl_counteragents_v2 AS
SELECT *,
trim('"' from (document->'type')::varchar) as dl_doc_type,
trim('"' from (document->'serial')::varchar)  as dl_doc_serial,
trim('"' from (document->'number')::varchar)  as dl_doc_number,
trim('"' from (document->'date')::varchar)   as dl_doc_date
FROM 
(SELECT 
    (jsonb_populate_record(NULL::dl_counteragent_v2, jsonb_array_elements(("values")::jsonb))).*
FROM ext.dl_counteragents_json) cnta;

\i cr-vw_dl_addr_contact_ext.sql
\i cr-vw_dl_addr_phone_ext.sql


/***
SELECT 
(jsonb_populate_record(NULL::dl_counteragent_v2, jsonb_array_elements(("values"->>'data')::jsonb))).*
FROM dl_counteragents_json;

***/
