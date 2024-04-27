-- DROP FUNCTION shp.fntr_dl_label_aiu();

CREATE OR REPLACE FUNCTION shp.fntr_dl_label_aiu()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE 
loc_shp_id integer;
loc_boxes integer;
BEGIN
    RAISE NOTICE 'shp.fntr_dl_label_aiu TG_OP=%, TG_WHEN=%', TG_OP, TG_WHEN;
    IF NEW.status = 'new' THEN
        SELECT s.shp_id, s.boxes INTO loc_shp_id, loc_boxes
        FROM shp.dl_preorder_params p
        JOIN shp.shipments s ON s.shp_id = p.shp_id 
        WHERE req_id=NEW.prereq_id; 

        EXECUTE pg_notify('ask_dl_label', format('%s %s %s', NEW.prereq_id, loc_shp_id, loc_boxes));
    ELSIF NEW.status = 'enqueued' THEN
        EXECUTE pg_notify('get_dl_label', format('%s %s %s', OLD.prereq_id, OLD.label_type, OLD.label_format));
    END IF;
    RETURN NEW;
END;
$function$
;

-- Permissions

ALTER FUNCTION shp.fntr_dl_label_aiu() OWNER TO arc_energo;
GRANT ALL ON FUNCTION shp.fntr_dl_label_aiu() TO public;
GRANT ALL ON FUNCTION shp.fntr_dl_label_aiu() TO arc_energo;

-- ##################################################3
/**
CREATE TRIGGER dl_labels_aiu AFTER INSERT OR UPDATE ON
shp.dl_labels_q FOR EACH ROW EXECUTE PROCEDURE fntr_dl_label_aiu();
**/
