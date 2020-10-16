--
DROP FUNCTION shp.dl_get_addr_details(integer);

CREATE OR REPLACE FUNCTION shp.dl_get_addr_details(arg_addr_id integer)
 -- RETURNS SETOF RECORD
 RETURNS TABLE(ret_type char, ret_id integer)
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = arc_energo
AS $function$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
  copy_cmd varchar;
begin
-- ./get-book-address.py --addr_id "$1" --log_level=INFO --log_to_file="$LOG"
    cmd := format('python3 %s/get-book-address.py --addr_id=%s --conf=%s/dl.conf --log_to_file=%s/get-book-address-%s.log --log_level=DEBUG', 
        wrk_dir, -- script dir
        arg_addr_id,
        wrk_dir, -- conf dir
        wrk_dir, -- logfile dir
        arg_addr_id);

    IF cmd IS NULL 
    THEN 
       err_str := 'get-book-address cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    -- RAISE NOTICE 'cmd=%', cmd;
    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;
    -- RAISE NOTICE 'ret_str=%, err_str=%', ret_str, err_str;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE 'get-book-address cmd=%^err_str=[%]', cmd, err_str; 
       RETURN;
    ELSE    
        create temporary table if not exists tmp_addr_contacts_json (like ext.dl_addr_contacts_json);
        truncate table tmp_addr_contacts_json;
        copy_cmd := format ('COPY tmp_addr_contacts_json(addr_id, jb) FROM %L (FORMAT CSV, DELIMITER "^")'
           , format('addr_%s.csv', arg_addr_id));
        -- RAISE NOTICE 'copy_cmd=%', copy_cmd;
        EXECUTE copy_cmd;
        /**
        EXECUTE format ('\COPY tmp_addr_contacts_json(addr_id, jb) FROM %L (FORMAT CSV, DELIMITER "^")'
           , format('addr_%s.csv', arg_addr_id));
        **/

        RETURN QUERY SELECT 'C'::char as ret_type,
        (jsonb_populate_record(NULL::shp.t_dl_contact, jsonb_array_elements(jsonb_array_elements(tmp_addr_contacts_json.jb) -> 'contacts'::text))).id AS ret_id
        FROM tmp_addr_contacts_json
        UNION
        SELECT 'P'::char,
        (jsonb_populate_record(NULL::shp.t_dl_phone, jsonb_array_elements(jsonb_array_elements(tmp_addr_contacts_json.jb) -> 'phones'::text))).id
        FROM tmp_addr_contacts_json;



    END IF;
    RETURN;
end
$function$
;

/**
-- \copy tmp_addr_contacts_json(addr_id, jb) from :csv with (format csv, delimiter '^');
\copy tmp_addr_contacts_json(addr_id, jb) from 'addr_18871665.csv' with (format csv, delimiter '^');

SELECT tmp_addr_contacts_json.addr_id,
to_timestamp(jsonb_array_elements(tmp_addr_contacts_json.jb) ->> 'lastUpdate'::text, 'YYYY-MM-DD"T"HH24:MI:SSZ'::text) AS lastupdate,
(jsonb_populate_record(NULL::t_dl_contact, jsonb_array_elements(jsonb_array_elements(tmp_addr_contacts_json.jb) -> 'contacts'::text))).id AS id,
(jsonb_populate_record(NULL::t_dl_contact, jsonb_array_elements(jsonb_array_elements(tmp_addr_contacts_json.jb) -> 'contacts'::text))).contact AS contact
FROM tmp_addr_contacts_json;
**/
