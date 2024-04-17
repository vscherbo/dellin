-- DROP FUNCTION shp.dl_label(integer, boolean);

CREATE OR REPLACE FUNCTION shp.dl_label(arg_req_id integer, arg_test boolean DEFAULT false)
  RETURNS character varying
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
  loc_app_srv varchar;
BEGIN
    cmd := format('python3 %s/dl_labels.py --log_file=%s/dl_labels.log --conf=%s --req_id=%s', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_req_id);

    IF cmd IS NULL 
    THEN 
       err_str := 'dl_label cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    loc_app_srv := arc_energo.arc_const('dellin_v2_server');
    SELECT * FROM public.exec_paramiko(loc_app_srv, '22', 'svc', cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL AND err_str <> ''
    THEN 
       RAISE NOTICE 'dl_label [%]', err_str;
       --ret_str := format('%s/%s', ret_str, err_str);
       ret_str := err_str;
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
