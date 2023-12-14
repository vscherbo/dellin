CREATE OR REPLACE FUNCTION shp.dl_verify_sent_order(
    arg_doc_id character varying -- dellin tracking number
    )
  RETURNS void
AS
$BODY$
DECLARE cmd character varying;
  ret_j jsonb;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_app_order_json.py --pg_srv=localhost --log_file=%s/dl_order_info.log --conf=%s --doc_id=''%s''', 
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

    -- parsing ret_str 
    -- RAISE NOTICE 'ret_str=%', to_json(ret_str);
    RAISE NOTICE 'ret_str=%', array_to_json(ret_str)->>'sender';

END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
