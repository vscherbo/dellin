CREATE TABLE shp.vs_dl_tracking (
    dl_tracking_id serial NOT NULL,
    tracking_code varchar NULL,
    shipment_dt timestamp NULL,
    dst_inn varchar NULL,
    src_inn varchar NULL,
    CONSTRAINT shp_tracker_pk PRIMARY KEY (dl_tracking_id)
)
WITH (
    OIDS=FALSE
) ;

/**
ALTER TABLE shp.vs_dl_tracking ADD sized_weight numeric NULL;
ALTER TABLE shp.vs_dl_tracking ADD sized_volume numeric NULL;
ALTER TABLE shp.vs_dl_tracking ADD shp_height numeric NULL;
ALTER TABLE shp.vs_dl_tracking ADD shp_width numeric NULL;
ALTER TABLE shp.vs_dl_tracking ADD shp_length numeric NULL;
ALTER TABLE shp.vs_dl_tracking ADD oversized_weight numeric NULL;
ALTER TABLE shp.vs_dl_tracking ADD oversized_volume numeric NULL;
ALTER TABLE shp.vs_dl_tracking ADD doc_date timestamp without time zone;
**/
