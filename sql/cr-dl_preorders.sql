-- DROP FUNCTION shp.dl_preorders();

CREATE OR REPLACE FUNCTION shp.dl_preorders(OUT shp_id integer, OUT dl_dt text, OUT doc_id text)
 RETURNS SETOF record
 LANGUAGE sql
AS $function$
SELECT p.shp_id, to_char(s.shipdate, 'YYYY-MM-DD'), p.req_id::text FROM shp.dl_preorder_params p
JOIN shp.shipments s ON s.shp_id = p.shp_id AND s.carr_doc IS NULL and s.shipdate IS NOT NULL
WHERE p.sts_code = 1; -- успешеный предзаказ
-- WHERE p.sts_code in (1, 10, 11); -- успешеный предзаказ, верифицирован и нет
-- COMMENT ON COLUMN shp.dl_preorder_params.sts_code IS '0 - исходный, 1 - успешно создан, 2 - тест,черновик, 9 - сбой создания, 10 - верифицирован, 11 - есть расхождения с фактом';
$function$


CREATE TRIGGER dl_preorder_params_au AFTER UPDATE ON
shp.dl_preorder_params FOR EACH ROW
WHEN (((old.sts_code <> new.sts_code)
    AND (new.sts_code = 1))) EXECUTE PROCEDURE fntr_dl_preorder_params_au();

