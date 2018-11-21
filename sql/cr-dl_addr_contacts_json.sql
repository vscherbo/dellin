-- Drop table

-- DROP TABLE shp.dl_addr_contacts_json

CREATE TABLE shp.dl_addr_contacts_json (
    id serial NOT NULL,
    addr_id int4 NULL,
    jb jsonb NULL,
    CONSTRAINT dl_addr_contacts_json_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE shp.dl_addr_contacts_json OWNER TO arc_energo;
GRANT ALL ON TABLE shp.dl_addr_contacts_json TO arc_energo;
