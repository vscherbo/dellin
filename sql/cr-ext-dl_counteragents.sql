-- Drop table

-- DROP TABLE ext.dl_counteragents

CREATE TABLE ext.dl_counteragents (
	id int4 NOT NULL,
	uid uuid NULL,
	"lastUpdate" timestamp NULL,
	"name" text NULL,
	form text NULL,
	"type" text NULL DEFAULT 'juridical'::text,
	inn varchar(12) NULL,
	"document" json NULL,
	"Email" text NULL,
	"Phone" text NULL,
	addresses int4 NULL,
	dl_doc_type varchar NULL,
	dl_doc_serial varchar NULL,
	dl_doc_number varchar NULL,
	dl_doc_date varchar NULL,
	status int4 NOT NULL DEFAULT 0,
	CONSTRAINT dl_counteragents_inn_un UNIQUE (inn),
	CONSTRAINT dl_counteragents_pk PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE ext.dl_counteragents OWNER TO arc_energo;
GRANT ALL ON TABLE ext.dl_counteragents TO arc_energo;
