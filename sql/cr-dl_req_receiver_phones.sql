CREATE OR REPLACE FUNCTION shp.dl_req_receiver_contacts(arg_shp_id integer)
 RETURNS SETOF integer
 LANGUAGE sql
AS $function$
SELECT delivery.contact_id AS rcv_contact_id
FROM shp.delivery INNER JOIN shp.ship_bills ON delivery.dlvr_id = ship_bills.dlvrid
WHERE ship_bills.shp_id=arg_shp_id;$function$
;
