#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
# import configparser
#from dl_app import DL_app
import dl_app

dl_app.parser.add_argument('--ca_id', type=int, required=True, help='ca_id') 
dl_app.parser.add_argument('--term_id', type=int, required=True, help='DL terminal_id') 
args = dl_app.parser.parse_args()

# TODO rename 'dl_addr' to 'app'
dl_addr = dl_app.DL_app(args=args, description='DL terminal as address add')
logging.info("args={}".format(args))

if dl_addr.login(auth=True):
    # Торговый Дом ЭнергоПрибор, ca_id=6619266
    dl_res = dl_addr.dl.dl_address_term_add(ca_id=args.ca_id, term_id=args.term_id)
    logging.info('dl_res={}'.format(dl_res))
    # OUTPUT: dl_res={'success': {'state': 'new', 'addressID': 89941747}}
    if dl_res is not None:
        if 'success' in dl_res:
            ret_addr_id = dl_res['success']['addressID']
            logging.info('state={}, addressID={}'.format(
                dl_res['success']['state'], ret_addr_id))
            if 'new' == dl_res['success']['state']:
                print(ret_addr_id, end='', flush=True)
                dl_addr.db_login()
                curs = dl_addr.conn.cursor()
                loc_sql = curs.mogrify('INSERT INTO ext.dl_addresses(ca_id, id, terminal_id, is_terminal, type, status) VALUES(%s,%s,%s,%s,%s,%s);', # lastUpdate=now()
                    (args.ca_id, ret_addr_id, args.term_id, True, 'delivery', 1  ))
                logging.info("loc_sql={}".format(loc_sql))
                curs.execute(loc_sql)
                dl_addr.conn.commit()
                # TODO return code
            else:
                logging.info('Not new!')
        else:
            logging.error('DL_ERROR={}'.format(dl_res))
    dl_addr.logout()
