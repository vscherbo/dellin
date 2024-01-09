--DROP FUNCTION shp.dl_prepaid(out int8, out timestamp, out int4);

CREATE OR REPLACE FUNCTION shp.dl_prepaid(OUT ext_id bigint
, OUT bill_no integer
, OUT dl_req_id integer
)
 RETURNS SETOF record
 LANGUAGE sql
AS $function$
SELECT 
pr.prep_id,
pr.bill_no, 
dpp.req_id FROM arc_energo.vw_rcpt_prepayed pr
join shp.ship_bills sb on sb.bill = pr.bill_no
join shp.dl_preorder_params dpp on dpp.shp_id = sb.shp_id 
where pr.carrier = 'Деловые линии'
and not exists (select 1 from cash.atol_rcpt_q where pr.prep_id = ext_id);
$function$
;

-- Permissions

ALTER FUNCTION shp.dl_prepaid(out int8, out timestamp, out int4) OWNER TO arc_energo;
GRANT ALL ON FUNCTION shp.dl_prepaid(out int8, out timestamp, out int4) TO arc_energo;

