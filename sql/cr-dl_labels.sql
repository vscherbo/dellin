-- DROP FUNCTION shp.dl_labels(integer, varchar);

CREATE OR REPLACE FUNCTION shp.dl_labels(arg_req_id integer, arg_mode varchar)
  RETURNS character varying
AS
$BODY$
DECLARE
cmd character varying;
ret_str VARCHAR := '';
err_str VARCHAR := '';
wrk_dir text := '/opt/dellin';
loc_app_srv varchar;
loc_shp_id integer;
loc_boxes integer;
loc_format varchar;
loc_type varchar;
loc_msg varchar;
loc_status varchar;
loc_err_flag boolean := 'f';
BEGIN
    -- prepare
    cmd := format('python3 %s/dl_labels.py --log_file=%s/dl_labels.log --conf=%s --req_id=%s --mode=%s', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_req_id,
        arg_mode);

    IF arg_mode = 'ask' THEN
       -- check right status of arg_req_id
       -- В обработке, Забор груза от адреса, Ожидает сдачи на терминал
       -- SELECT ???

       -- get boxes for arg_req_id
       SELECT shp_id, boxes INTO loc_shp_id, loc_boxes FROM shp.shipments
       WHERE shp_id=(SELECT shp_id FROM shp.dl_preorder_params WHERE req_id = arg_req_id);
       -- IF FOUND ???
       RAISE NOTICE 'mode=ask: shp_id=%, boxes=%', loc_shp_id, loc_boxes;
       cmd := format('%s --shp_id=% --boxes=%s', cmd, loc_shp_id, loc_boxes);
    ELSE
       -- get format, type for arg_req_id
       SELECT label_format, label_type INTO loc_format, loc_type FROM shp.dl_labels WHERE prereq_id = arg_req_id;
       RAISE NOTICE 'mode=get: format=%, type=%', loc_format, loc_type;
       cmd := format('%s --format=%s --type=%s', cmd, loc_format, loc_type);
    END IF;

    -- run cmd
    IF cmd IS NULL 
    THEN 
        err_str := 'dl_labels cmd IS NULL';
        RAISE '%', err_str ; 
    END IF;

    loc_app_srv := arc_energo.arc_const('dellin_v2_server');
    SELECT * FROM public.exec_paramiko(loc_app_srv, '22', 'svc', cmd) INTO ret_str, err_str ;

    -- parse result
    IF err_str IS NOT NULL AND err_str <> ''
    THEN 
        RAISE NOTICE 'dl_labels ERR:[%]', err_str;
        ret_str := format('%s/ERR:%s', COALESCE(ret_str,''), err_str);
        --ret_str := err_str;
        loc_err_flag := 't';
    END IF;

    RAISE NOTICE 'ret_str=%', ret_str;

    IF arg_mode = 'ask' THEN
        loc_status := 'enqueue';
        IF loc_err_flag THEN
            loc_msg := err_str;
            IF err_str NOT LIKE '%Запрос на передачу грузомест по заказу уже выполняется%' THEN
                loc_status := 'enqueue-err';
            END IF;
        END IF;
    ELSE -- get
        IF loc_err_flag THEN
            loc_status := 'get-err';
        ELSE
            loc_status := 'got';
        END IF;
    END IF;

    RAISE NOTICE 'loc_status=%, loc_msg=%', loc_status, loc_msg;
    -- update
    UPDATE shp.dl_label SET status = loc_status, err_msg = loc_msg, last_dt = now()
    WHERE prereq_id = arg_req_id;
    
    RETURN ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
