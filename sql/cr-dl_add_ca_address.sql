CREATE OR REPLACE FUNCTION shp.dl_add_ca_address(
    arg_ca_id integer -- shp.vw_dl_counteragents.id
    , arg_term_id integer -- shp.vw_dl_terminal.id
    )
  RETURNS character varying -- new address_id OR some OS message
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_app_address.py --pg_srv=localhost --log_file=%s/dl_add_ca_address.log --conf=%s --ca_id=%s --term_id=%s', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_ca_id,
        arg_term_id);

    IF cmd IS NULL 
    THEN 
       err_str := 'dl_add_ca_address cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE 'dl_add_ca_address cmd=%^err_str=[%]', cmd, err_str; 
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
