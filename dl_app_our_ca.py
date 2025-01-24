#!/usr/bin/env python
""" Get our firms countreragents info """

import json
import logging
import sys

import dl_app

args = dl_app.parser.parse_args()

app = dl_app.DL_app(args=args, description='DL counteragents info')
logging.info("args=%s", args)

INS_CA = """ INSERT INTO ext.dl_our_ca(uid, inn, firm_name) VALUES(%s,%s,%s)
ON CONFLICT (uid) DO UPDATE
set inn=EXCLUDED.inn, firm_name=EXCLUDED.firm_name; """

# ON CONFLICT DO NOTHING;"""

if app.login(auth=True):
    #arg = [].append(args.doc_id)
    dl_res = app.dl.dl_counteragents_v2(True)
    if dl_res is None:
        logging.error("dl_counteragents res is None")
    elif "errors" in dl_res.keys():
        logging.error("dl_counteragents errors=%s", dl_res["errors"])
    elif 200 == app.dl.status_code:
        logging.debug('counteragents=%s',
                json.dumps(dl_res["data"]["counteragents"], ensure_ascii=False, indent=4))
        res = []
        app.db_login()
        curs = app.conn.cursor()
        for ca in dl_res["data"]["counteragents"]:
            ca_info = {}
            ca_info["uid"] = ca["uid"]
            if ca_info["uid"] is not None:
                ca_info["inn"] = ca["inn"]
                ca_info["name"] = ca["name"]
                #print(f'{ca["uid"]}^{ca["inn"]}^{ca["name"]}')
                res.append(ca_info)
                # insert into PG
                loc_sql = curs.mogrify(INS_CA, (ca["uid"], ca["inn"], ca["name"]))
                logging.info("loc_sql=%s", loc_sql.decode('utf8'))
                curs.execute(loc_sql)

        app.conn.commit()
        # logging.info('res=%s', res)
    else:
        err_str = f'ERROR={app.dl.err_msg}'
        logging.error(err_str)
        print(err_str, file=sys.stderr, end='', flush=True)

    app.logout()
