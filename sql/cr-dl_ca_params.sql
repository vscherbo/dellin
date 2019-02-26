DROP TABLE shp.dl_ca_params;

CREATE TABLE shp.dl_ca_params (
    id serial NOT NULL,
    arc_code integer NOT NULL,
    any_address varchar NULL, -- произвольный адрес для ИП
    ca_name varchar NULL,
    legal_name varchar NULL,
    inn varchar NULL,
    opf_dl varchar NULL,
    opf_name varchar NULL,
    street_kladr varchar NULL,
    street varchar NULL,
    house varchar NULL,
    chk_result integer NOT NULL DEFAULT 0,
    CONSTRAINT dl_ca_params_pk PRIMARY KEY (id)
);
