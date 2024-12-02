-- DROP FUNCTION shp.dl_term_id(int4);

CREATE OR REPLACE FUNCTION shp.dl_term_id(arg_addr_id integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
loc_res integer;
BEGIN
SELECT terminal_id INTO loc_res FROM ext.dl_addresses WHERE id=arg_addr_id;
IF NOT FOUND THEN
  SELECT terminal_id INTO loc_res FROM shp.vw_dl_addresses WHERE id=arg_addr_id;
END IF;
RETURN loc_res;
END;$function$
;

-- Permissions

ALTER FUNCTION shp.dl_term_id(int4) OWNER TO arc_energo;
GRANT ALL ON FUNCTION shp.dl_term_id(int4) TO public;
GRANT ALL ON FUNCTION shp.dl_term_id(int4) TO arc_energo;
