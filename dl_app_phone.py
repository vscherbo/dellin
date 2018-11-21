#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
# import configparser
#from dl_app import DL_app
import dl_app

dl_app.parser.add_argument('--addr_id', type=int, required=True, help='ca addr_id') 
args = dl_app.parser.parse_args()

dl_phones = dl_app.DL_app(args=args, description='DL phone add')
logging.info(dl_phones)

dl_phones.login(auth=True)

# addr_id=20463457 : 194292, г. Санкт-Петербург 1-й Верхний пер, д. 12
# Торговый Дом ЭнергоПрибор
dl_res = dl_phones.dl.dl_phone_add(args.addr_id, '+7(921)-917-65 97')
logging.info('dl_res={}'.format(dl_res))
# OUTPUT: dl_res={'success': {'state': 'new', 'phoneID': 89941747}}
if 'success' in dl_res:
    logging.info('state={}, phoneID={}'.format(
        dl_res['success']['state'],
        dl_res['success']['phoneID']))
    print(dl_res['success']['phoneID'])
else:
    logging.error('ERROR={}'.format(dl_res))
        

dl_phones.dl.dl_logout()
