drop type shp.t_dl_address cascade;
create type shp.t_dl_address as (
"code" varchar(255),
"terminal_uid" varchar(255),
"region_name" varchar(255),
"contacts" integer,
"house" varchar(255),
"lastUpdate" timestamp,
"cityID" integer,
"code_type" varchar(255),
"street" varchar(255),
"city_name" varchar(255),
"address" varchar(255),
"phones" integer,
"is_terminal" boolean,
"type" varchar(255),
"terminal_id" integer,
"id" integer,
"city_code" varchar(255));

drop view IF EXISTS shp.vw_dl_addresses;
create or replace view shp.vw_dl_addresses as
select ca_id, (jsonb_populate_record(null::shp.t_dl_address, jsonb_array_elements(jb)->'address')).* from shp.dl_addresses_json

\i cr-vw_dl_addr_contact_ext.sql
\i cr-vw_dl_addr_phone_ext.sql

