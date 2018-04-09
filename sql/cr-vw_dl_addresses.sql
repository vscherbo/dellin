drop view shp.vw_dl_addresses;
create or replace view shp.vw_dl_addresses as
select ca_id, (jsonb_populate_record(null::shp.t_dl_address, jsonb_array_elements(jb)->'address')).* from shp.dl_addresses_json
