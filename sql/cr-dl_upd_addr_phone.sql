CREATE OR REPLACE FUNCTION shp.dl_upd_addr_phone(
    arg_phone_id integer
    , arg_phone character varying -- single phone number with length >=10
    , arg_add_num character varying(5) DEFAULT NULL -- single phone number with length <=5
    )
  RETURNS character varying -- new phone_id OR some OS message
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_app_phone_update.py --pg_srv=localhost --log_file=%s/dl_app_phone_update.log --conf=%s --phone_id=%s --phone=''%s''', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_phone_id,
        arg_phone);
    
    IF arg_add_num IS NOT NULL
    THEN
        cmd := format('%s --add_num=''%s''', cmd, arg_add_num );
    END IF;

    IF cmd IS NULL 
    THEN 
       err_str := 'dl_upd_addr_phone cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE 'dl_upd_addr_phone cmd=%^err_str=[%]', cmd, err_str; 
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
