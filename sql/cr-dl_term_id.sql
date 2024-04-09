-- DROP FUNCTION shp.dl_term_id(int4);

CREATE OR REPLACE FUNCTION shp.dl_term_id(arg_addr_id integer)
 RETURNS integer
 LANGUAGE sql
AS $function$
SELECT terminal_id AS RESULT FROM ext.dl_addresses WHERE id=arg_addr_id
UNION 
SELECT terminal_id FROM shp.vw_dl_addresses WHERE id=arg_addr_id;
$function$
;

-- Permissions

ALTER FUNCTION shp.dl_term_id(int4) OWNER TO arc_energo;
GRANT ALL ON FUNCTION shp.dl_term_id(int4) TO arc_energo;

