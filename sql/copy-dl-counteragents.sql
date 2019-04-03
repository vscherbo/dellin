-- drop backup table
DROP TABLE IF EXISTS ext.z_dl_counteragents_json;

-- create and copy from production table
CREATE TABLE ext.z_dl_counteragents_json AS SELECT * FROM ext.dl_counteragents_json;
-- comment to prevent pg_dump
COMMENT ON TABLE ext.z_dl_counteragents_json IS 'no_dump';

-- copy downloaded data into production table
TRUNCATE TABLE ext.dl_counteragents_json;
\copy ext.dl_counteragents_json FROM res-counteragents.txt;

-- truncate 'daily' table
TRUNCATE TABLE ext.dl_counteragents;
-- insert fresh data into 'daily' table
INSERT INTO  ext.dl_counteragents (SELECT * FROM shp.vw_dl_counteragents) ON CONFLICT DO NOTHING;

