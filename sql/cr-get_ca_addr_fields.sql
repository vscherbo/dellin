drop function shp.dl_ca_addr_fields(integer);
CREATE OR REPLACE FUNCTION shp.dl_ca_addr_fields(arg_code integer,
out ret_flg boolean,
out ret_street_code varchar,
out ret_addr_house varchar,
out ret_addr_block varchar,
out ret_addr_flat varchar
)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
declare
ret_addr_city varchar;
ret_addr_street varchar;
begin
    SELECT * FROM dadata_address(arg_code)
    into ret_flg, ret_addr_city, ret_addr_street, ret_addr_house, ret_addr_block, ret_addr_flat ;

    SELECT street_code into ret_street_code FROM ext.dl_streets ds 
    where ds.search_string = ret_addr_street
    AND ds.city_id IN (SELECT dp.city_id FROM ext.dl_places dp WHERE dp.search_string = ret_addr_city);

    RAISE NOTICE 'ret_flg=%, ret_street_code=%, ret_addr_house=%, ret_addr_block=%, ret_addr_flat=%', 
    ret_flg,
    ret_street_code,
    ret_addr_house,
    ret_addr_block,
    ret_addr_flat;

end;
$function$;

