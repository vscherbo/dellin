-- Drop table

-- DROP TABLE shp.dl_addresses_json

CREATE TABLE shp.dl_addresses_json (
	ca_id int4 NOT NULL,
	jb jsonb NULL,
	CONSTRAINT dl_addresses_json_pk PRIMARY KEY (ca_id)
);

-- Permissions

ALTER TABLE shp.dl_addresses_json OWNER TO arc_energo;
GRANT ALL ON TABLE shp.dl_addresses_json TO arc_energo;
