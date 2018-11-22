drop VIEW IF EXISTS shp.vw_dl_addr_contact_ext;
CREATE OR REPLACE VIEW shp.vw_dl_addr_contact_ext
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
    (jsonb_populate_record(NULL::shp.t_dl_contact, jsonb_array_elements(jsonb_array_elements(c.jb) -> 'contacts'::text))).id AS contact_id,
    (jsonb_populate_record(NULL::shp.t_dl_contact, jsonb_array_elements(jsonb_array_elements(c.jb) -> 'contacts'::text))).contact AS contact,
    to_timestamp(jsonb_array_elements(c.jb) ->> 'lastUpdate'::text, 'YYYY-MM-DD"T"HH24:MI:SSZ'::text) AS lastupdate
   FROM shp.vw_dl_counteragents ca
    LEFT JOIN shp.vw_dl_addresses a ON a.ca_id = ca.id AND a."type" = 'delivery'
    LEFT JOIN shp.dl_addr_contacts_json c ON c.addr_id = a.id;

-- Permissions
-- ALTER TABLE shp.vw_dl_addr_contact_ext OWNER TO arc_energo;
-- GRANT ALL ON TABLE shp.vw_dl_addr_contact_ext TO arc_energo;
