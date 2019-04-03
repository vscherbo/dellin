drop function shp.dl_ca_addr_fields(integer, varchar);
CREATE OR REPLACE FUNCTION shp.dl_ca_addr_fields(arg_code integer,
    arg_addr_text varchar DEFAULT NULL,
out ret_flg boolean,
out ret_street_code varchar,
out ret_addr_house varchar,
out ret_addr_block varchar,
out ret_addr_flat varchar,
out ret_addr_street varchar,
out ret_addr_street_type varchar,
out ret_addr_city_code varchar
)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
declare
ret_addr_city varchar;
begin
    SELECT * FROM dadata_address(arg_code, arg_addr_text)
    into ret_flg, ret_addr_city, ret_addr_city_code, ret_addr_street, ret_addr_street_type, ret_addr_house, ret_addr_block, ret_addr_flat ;

    IF ret_addr_street IS NULL THEN
        ret_addr_street := '';
        ret_addr_street_type := '';
    ELSE
        SELECT street_code into ret_street_code FROM ext.dl_streets ds 
        -- where ds.search_string = replace(ret_addr_street, 'ё', 'е')
        where ds.search_string ILIKE '%' || replace(ret_addr_street, 'ё', 'е') || '%'
        AND ds.city_id IN (SELECT dp.city_id FROM ext.dl_places dp WHERE dp.code LIKE ret_addr_city_code || '%');
    END IF;

    RAISE NOTICE 'ret_flg=%, ret_street_code=%, ret_addr_street=%, ret_addr_house=%, ret_addr_block=%, ret_addr_flat=%',
    ret_flg,
    ret_street_code,
    ret_addr_street,
    ret_addr_house,
    ret_addr_block,
    ret_addr_flat;

end;
$function$;

