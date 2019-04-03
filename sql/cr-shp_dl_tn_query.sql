--
DROP FUNCTION arc_energo.shp_dl_tn_query(in_query_dt timestamp without time ZONE);

CREATE OR REPLACE FUNCTION arc_energo.shp_dl_tn_query(in_query_dt timestamp without time zone DEFAULT now(), 
OUT dl_dt text, OUT sender_inn text, OUT receiver_inn text)
 RETURNS SETOF record
 LANGUAGE sql
AS $function$
SELECT dl_dt, dl_sender, dl_receiver AS RESULT FROM arc_energo.vw_dl_shipping
WHERE dl_dt::date = date_trunc('DAY', in_query_dt);
$function$
