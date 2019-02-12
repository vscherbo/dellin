drop VIEW IF EXISTS shp.vw_dl_addr_phone_ext;
CREATE OR REPLACE VIEW shp.vw_dl_addr_phone_ext
AS
SELECT
    a.address,
    a.is_terminal,
    a.terminal_uid,
    ca.form,
    ca.name,
    ca.inn,
    ca.id as ca_id,
    c.addr_id,
    (jsonb_populate_record(NULL::shp.t_dl_phone, jsonb_array_elements(jsonb_array_elements(c.jb) -> 'phones'::text))).id AS phone_id,
    (jsonb_populate_record(NULL::shp.t_dl_phone, jsonb_array_elements(jsonb_array_elements(c.jb) -> 'phones'::text))).phone AS phone,
    (jsonb_populate_record(NULL::shp.t_dl_phone, jsonb_array_elements(jsonb_array_elements(c.jb) -> 'phones'::text)))."phoneFormatted" AS "phoneFormatted",
    (jsonb_populate_record(NULL::shp.t_dl_phone, jsonb_array_elements(jsonb_array_elements(c.jb) -> 'phones'::text)))."addNumber" AS "addNumber",
    to_timestamp(jsonb_array_elements(c.jb) ->> 'lastUpdate'::text, 'YYYY-MM-DD"T"HH24:MI:SSZ'::text) AS lastupdate
   FROM shp.vw_dl_counteragents ca
    LEFT JOIN shp.vw_dl_addresses a ON a.ca_id = ca.id AND a."type" = 'delivery'
    LEFT JOIN ext.dl_addr_contacts_json c ON c.addr_id = a.id;

-- Permissions
-- ALTER TABLE shp.vw_dl_addr_phone_ext OWNER TO arc_energo;
-- GRANT ALL ON TABLE shp.vw_dl_addr_phone_ext TO arc_energo;
