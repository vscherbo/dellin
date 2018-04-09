-- create or replace view vw_dl_addresses as
select ca_id, (jsonb_populate_record(null::dl_address, jsonb_array_elements(jb)->'address')).* from dl_addresses_json