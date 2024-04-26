CREATE OR REPLACE FUNCTION shp.fntr_dl_preorder_params_au()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE 
loc_shp_id integer;
loc_boxes integer;
BEGIN
    INSERT INTO shp.dl_labels_q (prereq_id) VALUES(NEW.req_id);
    RAISE NOTICE 'shp.fntr_dl_preorder_params_au TG_OP=%, TG_WHEN=%', TG_OP, TG_WHEN;
    RETURN NEW;
END;
$function$
;


CREATE TRIGGER dl_preorder_params_au AFTER UPDATE ON
shp.dl_preorder_params FOR EACH ROW
WHEN (((old.sts_code <> new.sts_code)
    AND (new.sts_code = 1))) EXECUTE PROCEDURE fntr_dl_preorder_params_au();

