select 
(jsonb_populate_record(null::dl_terminals,
jsonb_array_elements(
(jsonb_populate_record(null::dl_terminals_city, jsonb_array_elements( jsonb_array_elements(values)->'city'))).terminals->'terminal'
)
)).* 
from dl_terminals_json