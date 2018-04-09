drop type dl_counteragent;
create type dl_counteragent as (
"id" integer,
"lastUpdate" timestamp,
"name" text,
"form" text,
"type" text,
"inn" text
-- "addresses" integer
);
