-- DROP FUNCTION shp.save_dl_conflict();

CREATE OR REPLACE FUNCTION shp.save_dl_conflict()
    RETURNS trigger
    LANGUAGE plpgsql
AS $function$
begin
    
    insert into dl_conflict values(default, default,
    old.dl_tracking_id, 
    old.tracking_code, old.shp_id, 
    new.tracking_code, new.shp_id);

    new.status := 0;

    return new;
end;
$function$
;

-- Permissions

--GRANT ALL ON FUNCTION shp.save_dl_conflict() TO arc;
;

-- Permissions

GRANT ALL ON FUNCTION shp.save_dl_conflict() TO arc_energo;
;
