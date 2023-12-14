DROP FUNCTION shp.dl_orders(character varying);

CREATE OR REPLACE FUNCTION shp.dl_orders(IN arg_docid character varying)
RETURNS text AS
$BODY$
import requests
import json

payload = {}
order_dict = {}
payload["docid"] = arg_docid
if not GD.has_key('dl_sessionID'):
    plpy.log('not logged in dl_api yet. Logging...')
    plpy.execute('select * from shp.dl_auth();')

payload['sessionID'] = GD['dl_sessionID']
payload['appKey'] = GD['dl_appKey']

GD['dl_payload'] = payload
host = "https://api.dellin.ru"
# res = plpy.execute('select * from shp.dl_api({0}/{1})'.format(host, 'v2/customers/orders.json'))
# res = plpy.execute("""select * from shp.dl_api('{0}');""".format("https://api.dellin.ru/v2/customers/orders.json"))
#s = """select * from shp.dl_api('{0}');""".format("https://api.dellin.ru/v2/customers/orders.json")
s = """select * from shp.dl_api('https://api.dellin.ru/v2/customers/orders.json');"""
res = plpy.execute(s)
# order_dict = eval(res[0]["ret_json_text"])
order_dict = GD['dl_text']

return order_dict

$BODY$
  LANGUAGE plpythonu VOLATILE
  COST 100;
