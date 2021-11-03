-- DROP FUNCTION shp.dl_add_counteragent(integer, varchar, varchar, varchar, varchar, boolean);

CREATE OR REPLACE FUNCTION shp.dl_add_counteragent(
    arg_code integer, -- Предприятия.Код
    arg_addr varchar DEFAULT NULL,
    arg_name varchar DEFAULT NULL,
    arg_form_name varchar DEFAULT NULL,
    arg_country_name varchar DEFAULT NULL,
    arg_juridical boolean DEFAULT NULL
    )
  RETURNS character varying AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
  loc_country_id varchar;
  loc_juridical boolean;
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

    IF arg_name IS NOT NULL THEN
        cmd := format('%s --name=''%s''', cmd, arg_name);
    END IF;

    IF arg_form_name IS NOT NULL THEN
        cmd := format('%s --form_name=''%s''', cmd, arg_form_name);
        --
        SELECT country_id INTO loc_country_id FROM shp.dl_countries 
        WHERE country_name = COALESCE(arg_country_name, 'Россия');
        IF NOT FOUND THEN
            RAISE 'Страна % не найдена в справочнике Деллин', arg_country_name ; 
        END IF;
        cmd := format('%s --country_id=''%s''', cmd, loc_country_id);
        --
        IF arg_juridical IS NOT NULL AND NOT arg_juridical THEN
            loc_juridical := 'False';
        ELSE
            loc_juridical := 'True';
        END IF;
        cmd := format('%s --juridical=''%s''', cmd, loc_juridical);
    END IF;

    IF cmd IS NULL 
    THEN 
       ret_str := 'dl_add_counteragent cmd IS NULL';
       RAISE '%', ret_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;
    RAISE NOTICE 'dl_add_counteragent cmd=[%]^ret_str=[%]^err_str=[%]', cmd, ret_str, err_str;

    IF err_str IS NOT NULL AND err_str <> ''
    THEN 
       RAISE NOTICE 'dl_add_counteragent cmd=%^err_str=[%]', cmd, err_str;
       ret_str := shp.dl_add_counteragent_free_addr(arg_code, arg_addr, arg_name, arg_form_name, arg_country_name, arg_juridical);
       err_str := NULL;
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
