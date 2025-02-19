CREATE OR REPLACE FUNCTION shp.dl_get_our_ca()
  RETURNS character varying -- err_str OR empty str
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
  loc_app_srv varchar;
BEGIN
    cmd := format('python3 %s/dl_app_our_ca.py --pg_srv=vm-pg.arc.world --log_file=%s/dl_get_our_ca.log --conf=%s', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir) -- conf file
        );

    IF cmd IS NULL 
    THEN 
       err_str := 'dl_get_our_ca cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    loc_app_srv := arc_energo.arc_const('dellin_v2_server');
    SELECT * FROM public.exec_paramiko(loc_app_srv, '22', 'svc', cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL AND err_str <> ''
    THEN 
       RAISE 'dl_get_our_ca cmd=%^err_str=[%]', cmd, err_str; 
       --ret_str := format('%s/%s', ret_str, err_str);
       ret_str := err_str;
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
