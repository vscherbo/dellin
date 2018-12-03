drop type shp.t_dl_terminals;

create type shp.t_dl_terminals as (
"isOffice" bool,
"isPVZ" bool,
name varchar(255),
"fullAddress" varchar(255),
id integer,
address varchar(255),
"maxWeight" numeric(9,2),
"maxHeight" numeric(9,2),
"maxLength" numeric(9,2),
"maxVolume" numeric(9,2),
"maxWidth" numeric(9,2)
);
