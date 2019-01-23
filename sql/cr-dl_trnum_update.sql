CREATE OR REPLACE FUNCTION shp.dl_trnum_update()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE
dl_tr record;
loc_RETURNED_SQLSTATE TEXT;
loc_MESSAGE_TEXT TEXT;
loc_PG_EXCEPTION_DETAIL TEXT;
loc_PG_EXCEPTION_HINT TEXT;
loc_PG_EXCEPTION_CONTEXT TEXT;
loc_result TEXT;
loc_status integer := -9;
loc_func_name text := 'dl_trnum_update';
begin
    for dl_tr in (select shp_id, shipment_dt, tracking_code, dl_tracking_id
                  from shp.vs_dl_tracking
                  where status = 0
                  order by tracking_code) 
    loop                
        begin
            update shp.shipments s set (carr_doc, carr_docdt) = (dl_tr.tracking_code, dl_tr.shipment_dt)
            where dl_tr.shp_id = s.shp_id;
            update "Счета" b set ("КодТК", "ДокТК", "ДокТКДата", "Отгружен") = (6, dl_tr.tracking_code, dl_tr.shipment_dt, true)
                where b."№ счета" in (SELECT sb.bill FROM shp.ship_bills sb WHERE sb.shp_id = dl_tr.shp_id);
            loc_status := 1;
            EXCEPTION WHEN OTHERS then
                GET STACKED DIAGNOSTICS
                loc_RETURNED_SQLSTATE = RETURNED_SQLSTATE,
                loc_MESSAGE_TEXT = MESSAGE_TEXT,
                loc_PG_EXCEPTION_DETAIL = PG_EXCEPTION_DETAIL,
                loc_PG_EXCEPTION_HINT = PG_EXCEPTION_HINT,
                loc_PG_EXCEPTION_CONTEXT = PG_EXCEPTION_CONTEXT ;
                loc_result = format(E'%s RETURNED_SQLSTATE=%s, MESSAGE_TEXT=%s,\nPG_EXCEPTION_DETAIL=%s,\nPG_EXCEPTION_HINT=%s,\nPG_EXCEPTION_CONTEXT=%s', loc_func_name, loc_RETURNED_SQLSTATE, loc_MESSAGE_TEXT, loc_PG_EXCEPTION_DETAIL, loc_PG_EXCEPTION_HINT, loc_PG_EXCEPTION_CONTEXT);
                RAISE NOTICE 'EXCEPTION=%', loc_result;
                loc_status := -1;
        end;
        update shp.vs_dl_tracking set status = loc_status, tracking_result = loc_result
        where shp.vs_dl_tracking.dl_tracking_id = dl_tr.dl_tracking_id;

        RAISE NOTICE 'dl_tr=%, loc_status=%, loc_result=%', dl_tr, loc_status, loc_result;
    end loop;
end;$function$
