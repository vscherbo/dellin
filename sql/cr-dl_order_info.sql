CREATE OR REPLACE FUNCTION shp.dl_order_info(
    arg_doc_id character varying -- dellin tracking number
    )
  RETURNS character varying -- arrival, sender, receiver as string with delimiter '^'
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_app_order.py --pg_srv=localhost --log_file=%s/dl_order_info.log --conf=%s --doc_id=''%s''', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_doc_id);

    IF cmd IS NULL 
    THEN 
       err_str := 'dl_order_info cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE 'dl_order_info cmd=%^err_str=[%]', cmd, err_str; 
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
