-- shp.dl_conflict определение

-- Drop table

-- DROP TABLE shp.dl_conflict;

CREATE TABLE shp.dl_conflict (
    id serial4 NOT NULL,
    dt_insert timestamp NOT NULL DEFAULT now(),
    old_dl_tracking_id int4 NULL,
    old_tracking_code varchar NULL,
    old_shp_id int4 NULL,
    new_tracking_code varchar NULL,
    new_shp_id int4 NULL,
    CONSTRAINT dl_conflict_pk PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE shp.dl_conflict OWNER TO arc_energo;
GRANT ALL ON TABLE shp.dl_conflict TO arc_energo;
