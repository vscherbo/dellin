drop type shp.t_dl_address;
create type shp.t_dl_address as (
"code" varchar(255),
"terminal_uid" varchar(255),
"region_name" varchar(255),
"contacts" integer,
"house" varchar(255),
"lastUpdate" timestamp,
"cityID" integer,
"code_type" varchar(255),
"street" varchar(255),
"city_name" varchar(255),
"address" varchar(255),
"phones" integer,
"is_terminal" boolean,
"type" varchar(255),
"id" integer,
"city_code" varchar(255));
