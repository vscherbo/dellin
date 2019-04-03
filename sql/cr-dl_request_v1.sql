CREATE OR REPLACE FUNCTION shp.dl_request_v1(arg_shp_id integer, arg_test boolean DEFAULT 'f')
  RETURNS character varying
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_app_req_v1.py --pg_srv=localhost --log_file=%s/dl_app_req_v1.log --conf=%s --shp_id=%s', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_shp_id);

    IF arg_test THEN
        cmd := format('%s --test=True', cmd);
    END IF;

    IF cmd IS NULL 
    THEN 
       err_str := 'dl_request_v1 cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE 'dl_request_v1 cmd=%^err_str=[%]', cmd, err_str;
       ret_str := format('%s/%s', ret_str, err_str);
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
