-- Drop table

-- DROP TABLE ext.dl_freight_type;

CREATE TABLE ext.dl_freight_type (
	uid varchar NOT NULL,
	description varchar NOT NULL,
	CONSTRAINT dl_freight_type_pkey PRIMARY KEY (uid)
);

