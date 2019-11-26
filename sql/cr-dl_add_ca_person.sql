-- Function: shp.dl_add_ca_person(character varying)

-- DROP FUNCTION shp.dl_add_ca_person(integer);

CREATE OR REPLACE FUNCTION shp.dl_add_ca_person(
    arg_pdoc_id integer -- shp.person_doc.pdoc_id
    )
  RETURNS character varying AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/dellin';
BEGIN
    cmd := format('python3 %s/dl_add_ca_person.py --pg_srv=localhost --log_file=%s/dl_add_ca_person.log --conf=%s --pdoc_id=%s', 
        wrk_dir, -- script dir
        wrk_dir, -- logfile dir
        format('%s/dl.conf', wrk_dir), -- conf file
        arg_pdoc_id);
    -- --conf= ... --log_level=INFO
    IF cmd IS NULL 
    THEN 
       ret_str := 'dl_add_ca_person cmd IS NULL';
       RAISE '%', ret_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd) INTO ret_str, err_str ;

    IF err_str IS NOT NULL
    THEN 
       RAISE 'dl_add_ca_person cmd=%^err_str=[%]', cmd, err_str; 
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
