-- DROP FUNCTION shp.dl_request_v2(integer, boolean);

CREATE OR REPLACE FUNCTION shp.dl_request_v2(arg_shp_id integer, arg_test boolean DEFAULT false)
  RETURNS character varying
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
  loc_app_srv varchar;
BEGIN
    cmd := format('python3 %s/dl_app_req.py --log_file=%s/dl_app_req_v2.log --conf=%s --shp_id=%s', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_shp_id);

    RAISE NOTICE 'dl_request_v2, test=%', arg_test;
    IF arg_test THEN
        cmd := format('%s --test=True', cmd);
    END IF;

    IF cmd IS NULL 
    THEN 
       err_str := 'dl_request_v2 cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    loc_app_srv := arc_energo.arc_const('dellin_v2_server');
    SELECT * FROM public.exec_paramiko(loc_app_srv, '22', 'svc', cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL AND err_str <> ''
    THEN 
       RAISE NOTICE 'dl_request_v2 [%]', err_str;
       --ret_str := format('%s/%s', ret_str, err_str);
       ret_str := err_str;
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
