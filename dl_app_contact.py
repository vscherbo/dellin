#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
# import configparser
#from dl_app import DL_app
import dl_app

dl_app.parser.add_argument('--addr_id', type=int, required=True, help='ca addr_id') 
dl_app.parser.add_argument('--contact', type=str, required=True, help='contact name') 
args = dl_app.parser.parse_args()

app = dl_app.DL_app(args=args, description='DL contact add')
logging.info("args={}".format(args))

app.login(auth=True)

# addr_id=20463457 : 194292, г. Санкт-Петербург 1-й Верхний пер, д. 12
# Торговый Дом ЭнергоПрибор
dl_res = app.dl.dl_contact_add(args.addr_id, args.contact)
logging.info('dl_res={}'.format(dl_res))
# OUTPUT: dl_res={'success': {'state': 'new', 'contactID': 89941747}}
if 200 == app.dl.status_code:
    if 'success' in dl_res:
        ret_contact_id = dl_res['success']['personID']
        logging.info('state={}, personID={}'.format(
            dl_res['success']['state'],
            ret_contact_id))
        print(ret_contact_id, end='', flush=True)
        app.db_login()
        curs = app.conn.cursor()
        loc_sql = curs.mogrify(u'INSERT INTO ext.dl_addr_contact(addr_id, id, contact, status) VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING;', # lastUpdate=now()
            (args.addr_id, ret_contact_id, args.contact, 1 ))
        logging.info(u"loc_sql={}".format(loc_sql))
        curs.execute(loc_sql)
        app.conn.commit()

    else:
        logging.error('ERROR={}'.format(dl_res))
else:
    logging.error('ERROR={}'.format(app.dl.err_msg))

app.logout()
