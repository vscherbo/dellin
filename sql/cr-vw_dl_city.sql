drop view shp.vw_dl_city;  

create view shp.vw_dl_city as  
select (jsonb_populate_record(null::shp.t_dl_terminals_city, jsonb_array_elements( jsonb_array_elements(values)->'city'))).* from ext.dl_terminals_json;
