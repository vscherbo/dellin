CREATE OR REPLACE FUNCTION shp.dl_book_delete(
    arg_cas varchar DEFAULT NULL,
    arg_addresses varchar DEFAULT NULL,
    arg_phones varchar DEFAULT NULL,
    arg_contacts varchar DEFAULT NULL
    )
  RETURNS character varying
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
  org_cmd text := 'python3 %s/dl_app_book_delete.py --pg_srv=localhost --log_file=%s/dl_app_book_delete.log --conf=%s';
BEGIN
    cmd := format(org_cmd,
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir) -- conf file
    );

    IF arg_cas IS NOT NULL THEN
        cmd := format('%s --cas=%s', cmd, arg_cas);                 
    END IF;                                                                      

    IF arg_addresses IS NOT NULL THEN
        cmd := format('%s --addresses=%s', cmd, arg_addresses);                 
    END IF;                                                                      

    IF arg_phones IS NOT NULL THEN
        cmd := format('%s --phones=%s', cmd, arg_phones);                 
    END IF;                                                                      

    IF arg_contacts IS NOT NULL THEN
        cmd := format('%s --contacts=%s', cmd, arg_contacts);                 
    END IF;                                                                      

    IF cmd = org_cmd THEN 
       err_str := 'dl_book_delete: nothing to delete!';
       RAISE '%', err_str ; 
    END IF;

    IF cmd IS NULL THEN 
       err_str := 'dl_book_delete cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE 'dl_book_delete cmd=%^err_str=[%]', cmd, err_str; 
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
