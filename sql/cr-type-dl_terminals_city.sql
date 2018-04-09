drop type shp.t_dl_terminals_city;
create type shp.t_dl_terminals_city as (
code varchar(255),
name  varchar(255),
url varchar(255),
"cityID" integer,
timeshift integer,
terminals jsonb
);
