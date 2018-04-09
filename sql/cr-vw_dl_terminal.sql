DROP VIEW shp.vw_dl_terminal;
CREATE VIEW shp.vw_dl_terminal as
WITH dl_city AS ( 
SELECT
    (
        jsonb_populate_record(null::shp.t_dl_terminals_city, 
            jsonb_array_elements( jsonb_array_elements(values)->'city')
        )
    ).*
from shp.dl_terminals_json)
SELECT "name" AS city, "cityID", (jsonb_populate_record(null::shp.t_dl_terminals, jsonb_array_elements(terminals->'terminal'))).* FROM dl_city;
