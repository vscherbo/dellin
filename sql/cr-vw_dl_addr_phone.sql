CREATE OR REPLACE VIEW shp.vw_dl_addr_phone
AS SELECT dl_addr_contacts_json.addr_id,
    to_timestamp(jsonb_array_elements(dl_addr_contacts_json.jb) ->> 'lastUpdate'::text, 'YYYY-MM-DD"T"HH24:MI:SSZ'::text) AS lastupdate,
    (jsonb_populate_record(NULL::shp.t_dl_phone, jsonb_array_elements(jsonb_array_elements(dl_addr_contacts_json.jb) -> 'phones'::text))).id AS id,
    (jsonb_populate_record(NULL::shp.t_dl_phone, jsonb_array_elements(jsonb_array_elements(dl_addr_contacts_json.jb) -> 'phones'::text))).phone AS phone,
    (jsonb_populate_record(NULL::shp.t_dl_phone, jsonb_array_elements(jsonb_array_elements(dl_addr_contacts_json.jb) -> 'phones'::text)))."phoneFormatted" AS "phoneFormatted",
    (jsonb_populate_record(NULL::shp.t_dl_phone, jsonb_array_elements(jsonb_array_elements(dl_addr_contacts_json.jb) -> 'phones'::text)))."addNumber" AS "addNumber"
   FROM shp.dl_addr_contacts_json;

-- Permissions

ALTER TABLE shp.vw_dl_addr_phone OWNER TO arc_energo;
GRANT ALL ON TABLE shp.vw_dl_addr_phone TO arc_energo;
