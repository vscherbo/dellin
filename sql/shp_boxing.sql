CREATE TABLE arc_energo.shp_boxing (
	boxing_id serial NOT NULL,
	shp_id int4 NOT NULL,
	bx_weight NUMERIC,
	bx_length NUMERIC,
	bx_width NUMERIC,
	bx_height NUMERIC, 
	PRIMARY KEY (boxing_id),
	FOREIGN KEY (shp_id) REFERENCES shp_shipment 
)
WITH (
	OIDS=FALSE
) ;