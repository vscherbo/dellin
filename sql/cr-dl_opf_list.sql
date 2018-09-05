-- Drop table

-- DROP TABLE shp.dl_opf_list

CREATE TABLE shp.dl_opf_list (
	uid text NULL,
	opf_name text NULL,
	juridical bool NULL,
	full_name text NULL,
	inn_length int4 NULL,
	country_id text NULL
)
WITH (
	OIDS=FALSE
) ;

-- Permissions

ALTER TABLE shp.dl_opf_list OWNER TO arc_energo;
GRANT ALL ON TABLE shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(tableoid) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(cmax) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(xmax) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(cmin) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(xmin) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(ctid) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(uid) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(opf_name) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(juridical) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(full_name) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(inn_length) ON shp.dl_opf_list TO arc_energo;
GRANT ALL, SELECT, INSERT, UPDATE, DELETE, REFERENCES(country_id) ON shp.dl_opf_list TO arc_energo;
