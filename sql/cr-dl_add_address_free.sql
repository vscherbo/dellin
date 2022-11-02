CREATE OR REPLACE FUNCTION shp.dl_add_address_free(
    arg_ca_id integer -- shp.vw_dl_counteragents.id
    , arg_address character varying -- address as text
    )
  RETURNS character varying -- new address_id OR some message
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_add_address_free.py --pg_srv=localhost --log_file=%s/dl_add_address_free.log --conf=%s --ca_id=%s --address=''%s''', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_ca_id,
        arg_address);

    IF cmd IS NULL 
    THEN 
       err_str := 'dl_add_address_free cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE NOTICE 'dl_add_address_free cmd=%^err_str=[%]', cmd, err_str; 
       RAISE 'err_str=[%]', err_str; 
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
