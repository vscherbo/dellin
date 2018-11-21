#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
# import configparser
#from dl_app import DL_app
import dl_app

dl_app.parser.add_argument('--ca_id', type=int, required=True, help='ca_id') 
dl_app.parser.add_argument('--term_id', type=int, required=True, help='DL terminal_id') 
args = dl_app.parser.parse_args()

dl_addr = dl_app.DL_app(args=args, description='DL terminal as address add')
logging.info(dl_addr)

dl_addr.login(auth=True)

# addr_id=20463457 : 194292, г. Санкт-Петербург 1-й Верхний пер, д. 12
# Торговый Дом ЭнергоПрибор, ca_id=6619266
dl_res = dl_addr.dl.dl_address_term_add(ca_id=args.ca_id, term_id=args.term_id)
logging.info('dl_res={}'.format(dl_res))
# OUTPUT: dl_res={'success': {'state': 'new', 'phoneID': 89941747}}
if 'success' in dl_res:
    logging.info('state={}, addressID={}'.format(
        dl_res['success']['state'],
        dl_res['success']['addressID']))
    print(dl_res['success']['addressID'])
else:
    logging.error('ERROR={}'.format(dl_res))

dl_addr.logout()
