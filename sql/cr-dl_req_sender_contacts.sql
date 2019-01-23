CREATE OR REPLACE FUNCTION shp.dl_req_sender_contacts(arg_shp_id integer)
 RETURNS SETOF integer
 LANGUAGE sql
AS $function$
SELECT dl_addr_contact.id AS snd_contact_id
FROM (ext.dl_addresses INNER JOIN shp.shipments ON ext.dl_addresses.id = shipments.firm_addr_id) INNER JOIN ext.dl_addr_contact 
ON ext.dl_addresses.id = dl_addr_contact.addr_id
WHERE shipments.shp_id=arg_shp_id;
$function$
;
