-- Function: shp.dl_add_counteragent(character varying)

-- DROP FUNCTION shp.dl_add_counteragent(integer);

CREATE OR REPLACE FUNCTION shp.dl_add_counteragent(
    arg_code integer -- Предприятия.Код
    )
  RETURNS character varying AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_add_counteragent.py --pg_srv=localhost --log_to_file=%s/dl_add_counteragent.log --conf=%s --code=%s', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_code);
    -- --conf= ... --log_level=INFO
    IF cmd IS NULL 
    THEN 
       ret_str := 'dl_add_counteragent cmd IS NULL';
       RAISE '%', ret_str ; 
    END IF;

    -- ret_str := public.exec_paramiko(site, 22, 'uploader'::VARCHAR, cmd);
    ret_str := public.shell(cmd);
    
    IF ret_str <> ''
    THEN 
       RAISE 'dl_add_counteragent cmd=%^ret_str=[%]', cmd, ret_str; 
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
