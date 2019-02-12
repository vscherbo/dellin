DROP FUNCTION shp.dl_req_params(arg_shp_id integer, OUT snd_ca_id integer, OUT snd_addr_id integer, OUT rcv_ca_id integer, OUT rcv_addr_id integer, OUT boxes integer);
-- DROP FUNCTION shp.dl_req_params(arg_shp_id integer, OUT snd_ca_id integer, OUT snd_addr_id integer, OUT rcv_ca_id integer, OUT rcv_addr_id integer, OUT boxes integer, OUT pre_shipdate date);
CREATE OR REPLACE FUNCTION shp.dl_req_params(arg_shp_id integer, OUT snd_ca_id integer, OUT snd_addr_id integer, OUT rcv_ca_id integer, OUT rcv_addr_id integer, OUT boxes integer, OUT pre_shipdate date)
 RETURNS record
 LANGUAGE sql
AS $function$
SELECT dl_addresses_1.ca_id AS snd_ca_id, shipments.firm_addr_id AS snd_addr_id, dl_addresses.ca_id AS rcv_ca_id, 
delivery.dlvr_addr_id AS rcv_addr_id, shipments.boxes, 
(SELECT pre_shipdate::date AS pre_shipdate FROM shp.dl_preorder_params WHERE shp_id=arg_shp_id) 
FROM ext.dl_addresses AS dl_addresses_1 INNER JOIN (((shp.delivery INNER JOIN shp.ship_bills ON delivery.dlvr_id = ship_bills.dlvrid) 
INNER JOIN ext.dl_addresses ON delivery.dlvr_addr_id = dl_addresses.id) 
INNER JOIN shp.shipments ON ship_bills.shp_id = shipments.shp_id) ON dl_addresses_1.id = shipments.firm_addr_id
WHERE ship_bills.shp_id=arg_shp_id
$function$
;
