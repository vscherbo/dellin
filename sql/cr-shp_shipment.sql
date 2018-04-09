CREATE TABLE arc_energo.shp_shipment (
	shp_id serial NOT NULL,
	firm_code text NOT NULL,
	cons_id int4 NOT NULL,
	fact_dt timestamp NULL,
	shipper_id int4 NOT NULL,
	tn text NULL,
	status int4 NOT NULL DEFAULT 0,
	cons_type int4 NOT NULL DEFAULT 1,
	tn_dt timestamp NULL,
	PRIMARY KEY (shp_id),
	FOREIGN KEY (firm_code) REFERENCES "Фирма"("КлючФирмы")
)
WITH (
	OIDS=FALSE
) ;
COMMENT ON COLUMN arc_energo.shp_shipment.firm_code IS 'Код Фирмы-отправителя' ;
COMMENT ON COLUMN arc_energo.shp_shipment.cons_id IS 'id грузополучателя (cons_type)' ;
COMMENT ON COLUMN arc_energo.shp_shipment.status IS '0 - нужен запрос, 1 - ответ получен, 2 - ошибка запроса' ;
COMMENT ON COLUMN arc_energo.shp_shipment.cons_type IS '1 - cons_id=Код, 2 - shp_consignee.cons_id' ;
