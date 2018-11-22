CREATE OR REPLACE FUNCTION shp.dl_add_addr_phone(
    arg_addr_id integer -- shp.vw_dl_addresses.id
    , arg_phone character varying -- single phone number with length >=10
    )
  RETURNS character varying -- new phone_id OR some OS message
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_app_phone.py --pg_srv=localhost --log_file=%s/dl_add_addr_phone.log --conf=%s --addr_id=%s --phone=''%s''', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_addr_id,
        arg_phone);

    IF cmd IS NULL 
    THEN 
       err_str := 'dl_add_addr_phone cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE 'dl_add_addr_phone cmd=%^err_str=[%]', cmd, err_str; 
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
