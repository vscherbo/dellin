DROP VIEW shp.vw_dl_terminal;

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

CREATE VIEW shp.vw_dl_terminal as
WITH dl_city AS ( 
SELECT
    (
        jsonb_populate_record(null::shp.t_dl_terminals_city, 
            jsonb_array_elements( jsonb_array_elements(values)->'city')
        )
    ).*
from ext.dl_terminals_json)
SELECT "name" AS city, "cityID", (jsonb_populate_record(null::shp.t_dl_terminals, jsonb_array_elements(terminals->'terminal'))).* FROM dl_city;
