CREATE OR REPLACE FUNCTION shp.dl_req_sender_phones(arg_shp_id integer)
 RETURNS SETOF integer
 LANGUAGE sql
AS $function$
SELECT dl_addr_phone.id AS snd_phone_id
FROM (ext.dl_addresses INNER JOIN shp.shipments ON ext.dl_addresses.id = shipments.firm_addr_id) INNER JOIN ext.dl_addr_phone 
ON ext.dl_addresses.id = dl_addr_phone.addr_id
WHERE shipments.shp_id=arg_shp_id;$function$
;
