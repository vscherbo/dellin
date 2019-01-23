--
DROP FUNCTION shp.dl_trnum_query(in_query_dt timestamp without time ZONE);

CREATE OR REPLACE FUNCTION shp.dl_trnum_query(in_query_dt timestamp without time zone DEFAULT now(),
    OUT shp_id integer, OUT sender_inn text, OUT receiver_inn text, OUT dl_dt text)
 RETURNS SETOF record
 LANGUAGE sql
AS $function$
-- ignore INPUT arg !!!
--SELECT shp_id, snd_inn, rcv_inn, to_char(shipdate, 'YYYY-MM-DD') AS RESULT FROM shp.vw_dl_trnum_query;
/**/
SELECT distinct s.shp_id 
--    , sb.bill, b."Код", b.фирма
    , f."Ф_ИНН" as src_inn
    , e."ИНН" as dst_inn
    , to_char(s.shipdate, 'YYYY-MM-DD')
--    ,b."КодТК", b."ДокТК", b."ДокТКДата"
   from shp.shipments s 
     join shp.ship_bills sb ON sb.shp_id = s.shp_id
     join Счета b on sb.bill = b."№ счета"
     join shp.delivery d on sb.dlvrid = d.dlvr_id 
     join "Предприятия" e on e."Код" = b."Код" 
     join "Фирма" f on f."КлючФирмы" = b."фирма" 
  WHERE s.shipdate > '2018-12-06' and d.carr_id = 6
        and (s.carr_doc IS null or s.carr_doc = '')
        and e."ИНН" <> '000000000000'
  -- WHERE s.shipdate IS NOT NULL AND s.carr_doc IS NULL
/**/
$function$
