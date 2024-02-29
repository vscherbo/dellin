-- Drop table

-- DROP TABLE ext.dl_request_services;

CREATE TABLE ext.dl_request_services (
	id integer,
	uid varchar NOT NULL,
	"name" varchar NOT NULL,
	CONSTRAINT dl_request_services_pkey PRIMARY KEY (id)
);

