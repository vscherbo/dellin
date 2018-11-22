CREATE OR REPLACE FUNCTION shp.dl_add_addr_contact(
    arg_addr_id integer -- shp.vw_dl_addresses.id
    , arg_contact character varying -- single contact number with length >=10
    )
  RETURNS character varying -- new contact_id OR some OS message
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_app_contact.py --pg_srv=localhost --log_file=%s/dl_add_addr_contact.log --conf=%s --addr_id=%s --contact=''%s''', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_addr_id,
        arg_contact);

    IF cmd IS NULL 
    THEN 
       err_str := 'dl_add_addr_contact cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE 'dl_add_addr_contact cmd=%^err_str=[%]', cmd, err_str; 
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
