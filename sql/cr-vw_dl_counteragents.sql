-- 
drop view shp.vw_dl_counteragents cascade;

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
"document" json,
"Email" varchar,
"Phone" varchar,
"addresses" integer
);


CREATE OR REPLACE VIEW shp.vw_dl_counteragents
AS SELECT cnta.id,
    cnta.uid,
    cnta."lastUpdate",
    cnta.name,
    cnta.form,
    cnta.type,
    cnta.inn,
--    cnta.document,
    cnta."Email",
    cnta."Phone",
    cnta.addresses,
    btrim(((cnta.document -> 'type'::text)::character varying)::text, '"'::text) AS dl_doc_type,
    btrim(((cnta.document -> 'serial'::text)::character varying)::text, '"'::text) AS dl_doc_serial,
    btrim(((cnta.document -> 'number'::text)::character varying)::text, '"'::text) AS dl_doc_number,
    btrim(((cnta.document -> 'date'::text)::character varying)::text, '"'::text) AS dl_doc_date
   FROM ( 
SELECT (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text)).id AS id,
       (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text)).uid AS uid,
       (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text))."lastUpdate" AS "lastUpdate",
       (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text)).name AS name,
       (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text)).form AS form,
       (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text)).type AS type,
       (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text)).inn AS inn,
       (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text)).document AS document,
       (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text))."Email" AS "Email",
       (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text))."Phone" AS "Phone",
       (jsonb_populate_record(NULL::shp.dl_counteragent, jsonb_array_elements(dl_counteragents_json."values") -> 'counteragent'::text)).addresses AS addresses
           FROM ext.dl_counteragents_json) cnta;


\i sql/cr-vw_dl_addr_contact_ext.sql
\i sql/cr-vw_dl_addr_phone_ext.sql
