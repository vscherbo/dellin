#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
import sys
import dl_app

dl_app.parser.add_argument('--ca_id', type=int, required=True, help='ca_id') 
dl_app.parser.add_argument('--term_id', type=int, required=True, help='DL terminal_id') 
args = dl_app.parser.parse_args()

# TODO rename 'app' to 'app'
app = dl_app.DL_app(args=args, description='DL terminal as address add')
logging.info("args={}".format(args))

if app.login(auth=True):
    # Торговый Дом ЭнергоПрибор, ca_id=6619266
    dl_res = app.dl.dl_address_term_add(ca_id=args.ca_id, term_id=args.term_id)
    logging.info('dl_res={}'.format(dl_res))
    # OUTPUT: dl_res={'success': {'state': 'new', 'addressID': 89941747}}
    if 200 == app.dl.status_code:
        if 'success' in dl_res:
            ret_addr_id = dl_res['success']['addressID']
            logging.info('state={}, addressID={}'.format(dl_res['success']['state'], ret_addr_id))
            if 'new' == dl_res['success']['state'] or 'existing' == dl_res['success']['state']:
                print(ret_addr_id, end='', flush=True)
                app.db_login()
                curs = app.conn.cursor()
                loc_sql = curs.mogrify('INSERT INTO ext.dl_addresses(ca_id, id, terminal_id, is_terminal, type, status) VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;', # lastUpdate=now()
                    (args.ca_id, ret_addr_id, args.term_id, True, 'delivery', 1  ))
                logging.info("loc_sql={}".format(loc_sql))
                curs.execute(loc_sql)
                app.conn.commit()
                # TODO return code
            else:
                logging.info('Other...')
        else:
            err_str = 'ERROR={}'.format(dl_res)
            logging.error(err_str)
            print(err_str, file=sys.stderr, end='', flush=True)
    else:
        err_str = 'ERROR={}'.format(app.dl.err_msg)
        logging.error(err_str)
        print(err_str, file=sys.stderr, end='', flush=True)

    app.logout()
