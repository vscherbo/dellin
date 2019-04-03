-- Function: shp.dl_add_counteragent(character varying)

-- DROP FUNCTION shp.dl_add_counteragent(integer);

CREATE OR REPLACE FUNCTION shp.dl_add_counteragent(
    arg_code integer, -- Предприятия.Код
    arg_addr varchar DEFAULT NULL
    )
  RETURNS character varying AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_add_counteragent.py --pg_srv=localhost --log_file=%s/dl_add_counteragent.log --conf=%s --code=%s', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_code);
    -- --conf= ... --log_level=INFO

    IF arg_addr IS NOT NULL THEN
        cmd := format('%s --address=''%s''', cmd, arg_addr);
    END IF;

    IF cmd IS NULL 
    THEN 
       ret_str := 'dl_add_counteragent cmd IS NULL';
       RAISE '%', ret_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;

    IF err_str IS NOT NULL
    THEN 
       RAISE 'dl_add_counteragent cmd=%^ret_str=[%]', cmd, ret_str; 
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
