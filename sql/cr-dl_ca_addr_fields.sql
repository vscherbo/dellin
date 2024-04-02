--drop function shp.dl_ca_addr_fields(integer, varchar);

CREATE OR REPLACE FUNCTION shp.dl_ca_addr_fields(arg_code integer,
    arg_addr_text varchar DEFAULT NULL,
out ret_flg boolean,
out ret_street_code varchar,
out ret_addr_house varchar,
out ret_addr_block varchar,
out ret_addr_flat varchar,
out ret_addr_street varchar,
out ret_addr_street_type varchar,
out ret_addr_city_code varchar,
out ret_addr_city varchar
)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
DECLARE
    street_with_type varchar;
begin
    SELECT * FROM dadata_address_ext(arg_code, arg_addr_text)
    into ret_flg, ret_addr_city, ret_addr_city_code, ret_addr_street, ret_addr_street_type, street_with_type, ret_addr_house, ret_addr_block, ret_addr_flat ;

    IF ret_addr_street IS NULL THEN
        ret_addr_street := '';
        ret_addr_street_type := '';
    ELSE
        RAISE NOTICE 'ret_addr_street=%, ret_addr_street_type=%, street_with_type=[%]', ret_addr_street, ret_addr_street_type, street_with_type;
        SELECT street_code into ret_street_code FROM ext.dl_streets ds 
        -- OLD where ds.search_string ILIKE '%' || replace(ret_addr_street, 'ё', 'е') || '%'
        -- where ds.street_name ILIKE '%' || replace(street_with_type, 'ё', 'е') || '%'
        where ds.street_name = street_with_type
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

