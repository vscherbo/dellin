-- DROP FUNCTION shp.dl_preorders();

CREATE OR REPLACE FUNCTION shp.dl_preorders(OUT shp_id integer, OUT dl_dt text, OUT doc_id text)
 RETURNS SETOF record
 LANGUAGE sql
AS $function$
SELECT p.shp_id, to_char(s.shipdate, 'YYYY-MM-DD'), p.req_id::text FROM shp.dl_preorder_params p
JOIN shp.shipments s ON s.shp_id = p.shp_id AND s.carr_doc IS NULL and s.shipdate IS NOT NULL
WHERE p.sts_code = 1; -- успешеный предзаказ и не черновик
-- WHERE p.req_id is NOT NULL;
--WHERE p.req_id = 14203091;
$function$
