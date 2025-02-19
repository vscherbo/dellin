-- ext.dl_our_ca определение

-- Drop table

-- DROP TABLE ext.dl_our_ca;

CREATE TABLE ext.dl_our_ca (
	uid uuid NOT NULL,
	inn varchar NOT NULL,
	firm_name varchar NOT NULL,
	active bool DEFAULT true NULL,
	dt_change timestamp DEFAULT now() NULL,
	CONSTRAINT dl_our_ca_pk PRIMARY KEY (uid)
);
