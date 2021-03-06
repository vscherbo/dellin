#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
import sys
import dl_app

dl_app.parser.add_argument('--addr_id', type=int, required=True, help='ca addr_id')
dl_app.parser.add_argument('--phone', type=str, required=True, help='phone number')
dl_app.parser.add_argument('--add_num', type=str, required=False, help='extention number')
args = dl_app.parser.parse_args()

app = dl_app.DL_app(args=args, description='DL phone add')
logging.info("args={}".format(args))

if app.login(auth=True):
    # addr_id=20463457 : 194292, г. Санкт-Петербург 1-й Верхний пер, д. 12
    # Торговый Дом ЭнергоПрибор
    # dl_res = app.dl.dl_phone_add(args.addr_id, '+7(921)-917-65 97')
    dl_res = app.dl.dl_phone_add(args.addr_id, args.phone, args.add_num)
    logging.info('dl_res={}'.format(dl_res))
    # OUTPUT: dl_res={'success': {'state': 'new', 'phoneID': 89941747}}
    if 200 == app.dl.status_code:
        if 'success' in dl_res:
            ret_phone_id = dl_res['success']['phoneID']
            logging.info('state={}, phoneID={}'.format(
                dl_res['success']['state'],
                ret_phone_id))
            print(ret_phone_id, end='', flush=True)
            app.db_login()
            curs = app.conn.cursor()

            if args.add_num:
                loc_sql = curs.mogrify('INSERT INTO ext.dl_addr_phone(addr_id, id, phone, "addNumber", status) VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;',
                    (args.addr_id, ret_phone_id, args.phone, args.add_num, 1 ))
            else:
                loc_sql = curs.mogrify('INSERT INTO ext.dl_addr_phone(addr_id, id, phone, status) VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING;',
                    (args.addr_id, ret_phone_id, args.phone, 1 ))


            logging.info("loc_sql={}".format(loc_sql))
            curs.execute(loc_sql)
            app.conn.commit()
            
        else:
            err_str = 'ERROR={}'.format(dl_res)
            logging.error(err_str)
            print(err_str, file=sys.stderr, end='', flush=True)
    else:
        err_str = 'ERROR={}'.format(app.dl.err_msg)
        logging.error(err_str)
        print(err_str, file=sys.stderr, end='', flush=True)

    app.logout()
