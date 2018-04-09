SELECT ca.id, ca."lastUpdate", "name", form, ca."type", inn, adr.type, address
FROM vw_dl_counteragents ca
join vw_dl_addresses adr on ca.id = ca_id
;
