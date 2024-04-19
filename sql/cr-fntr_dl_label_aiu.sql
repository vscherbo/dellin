-- DROP FUNCTION shp.fntr_dl_label_aiu();

CREATE OR REPLACE FUNCTION shp.fntr_dl_label_aiu()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE 
ret_str varchar;
loc_msg varchar;                                                                                     
loc_status varchar;
BEGIN
	EXECUTE pg_notify('get_dl_label', format('%s^%s', TG_OP, NEW.prereq_id));
	RETURN NEW;
END;
$function$
;

-- Permissions

ALTER FUNCTION shp.fntr_dl_label_aiu() OWNER TO arc_energo;
GRANT ALL ON FUNCTION shp.fntr_dl_label_aiu() TO public;
GRANT ALL ON FUNCTION shp.fntr_dl_label_aiu() TO arc_energo;

