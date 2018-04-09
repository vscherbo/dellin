CREATE OR REPLACE FUNCTION shp.dl_set_tracking()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
declare
dl_tr record;
bill record;
loc_RETURNED_SQLSTATE TEXT;
loc_MESSAGE_TEXT TEXT;
loc_PG_EXCEPTION_DETAIL TEXT;
loc_PG_EXCEPTION_HINT TEXT;
loc_PG_EXCEPTION_CONTEXT TEXT;
loc_result_full TEXT;
loc_result TEXT;
loc_status integer := -1;
loc_func_name text := 'dl_trackin update Счета';
loc_tc text := '';
begin
    for dl_tr in (select s."№ счета", t.shipment_dt, t.tracking_code, t.tracking_result 
            from shp.vs_dl_tracking t
            join vw_dl_shipping s on s.dl_dt = t.shipment_dt::text 
                and s.dl_sender = t.src_inn and s.dl_receiver = t.dst_inn order by t.tracking_code) 
    loop                
        /** TEST **
        select b."Код", b."№ счета", b."Дата счета" into bill from "Счета" b
        where b."№ счета" = dl_tr."№ счета";
        RAISE NOTICE 'Счёт=%, tracking=%', bill, dl_tr.tracking_code;
        ***/

        /** UPDATE **/
        RAISE NOTICE 'lc_tc=%, tracking_code=%', loc_tc, dl_tr.tracking_code;
        if loc_tc <> dl_tr.tracking_code then 
            loc_tc := dl_tr.tracking_code;
            loc_result_full := NULL;
        end if;
        begin
            update "Счета" b set ("КодТК", "ДокТК", "ДокТКДата", "Отгружен") = (6, dl_tr.tracking_code, dl_tr.shipment_dt, true)
                where b."№ счета" = dl_tr."№ счета";
            loc_status := 1;
            loc_result := dl_tr."№ счета"::varchar;
            EXCEPTION WHEN OTHERS then
                GET STACKED DIAGNOSTICS
                loc_RETURNED_SQLSTATE = RETURNED_SQLSTATE,
                loc_MESSAGE_TEXT = MESSAGE_TEXT,
                loc_PG_EXCEPTION_DETAIL = PG_EXCEPTION_DETAIL,
                loc_PG_EXCEPTION_HINT = PG_EXCEPTION_HINT,
                loc_PG_EXCEPTION_CONTEXT = PG_EXCEPTION_CONTEXT ;
                loc_result = format(E'%s RETURNED_SQLSTATE=%s, MESSAGE_TEXT=%s,\nPG_EXCEPTION_DETAIL=%s,\nPG_EXCEPTION_HINT=%s,\nPG_EXCEPTION_CONTEXT=%s', loc_func_name, loc_RETURNED_SQLSTATE, loc_MESSAGE_TEXT, loc_PG_EXCEPTION_DETAIL, loc_PG_EXCEPTION_HINT, loc_PG_EXCEPTION_CONTEXT);
                RAISE NOTICE 'EXCEPTION=%', loc_result;
                loc_status := -2;
        end;
        loc_result_full := concat_ws('^', loc_result_full, loc_result);
        update shp.vs_dl_tracking set status = loc_status, tracking_result = loc_result_full
        where shp.vs_dl_tracking.tracking_code = dl_tr.tracking_code;

        /***/
        RAISE NOTICE 'dl_tr=%, loc_result_full=%, loc_result=%', dl_tr,loc_result_full, loc_result;
    end loop;
end;$function$
