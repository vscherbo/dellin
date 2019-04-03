CREATE OR REPLACE FUNCTION shp.dl_req_shipments()
 RETURNS SETOF integer
 LANGUAGE sql
AS $function$
SELECT shipments.shp_id
FROM (shp.delivery INNER JOIN (shp.ship_bills INNER JOIN shp.shipments ON ship_bills.shp_id = shipments.shp_id) 
ON delivery.dlvr_id = ship_bills.dlvrid) INNER JOIN shp.consignee ON delivery.csn_id = consignee.csn_id
WHERE consignee.kod<>223719 AND delivery.term_id Is Not Null AND shipments.packdate Is Not Null And shipments.packdate>'2019-01-20' 
AND shipments.shipdate Is Null AND delivery.carr_id=6;
$function$
;
