-- shp.dl_labels_q определение

-- Drop table

-- DROP TABLE shp.dl_labels_q;

CREATE TABLE shp.dl_labels_q (
	prereq_id int4 NOT NULL,
	status varchar NULL, -- new, enqueued, enqueue-err, got, get-err
	label_type varchar DEFAULT 'pdf'::character varying NOT NULL,
	label_format varchar DEFAULT '80x50'::character varying NOT NULL,
	err_msg varchar NULL,
	last_dt timestamp DEFAULT now() NULL,
	CONSTRAINT dl_labels_q_pk PRIMARY KEY (prereq_id)
);

-- Column comments

COMMENT ON COLUMN shp.dl_labels_q.status IS 'new, enqueued, enqueue-err, got, get-err';
