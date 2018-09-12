#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from shp_dellin import DellinAPI
# import psycopg2

ark_appkey = '08A8347F-8EA9-45FB-A8A3-518659DF9F41'
user = 'dellin@kipspb.ru'
pw = ')per-dellin'

log_format = '[%(filename)-21s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'
logging.basicConfig(filename='counters.log', format=log_format, level=logging.DEBUG)

dl = DellinAPI(ark_appkey, user, pw)
logging.info("logged in sess_id={0}".format(dl.sessionID))


counteragents_res = dl.dl_book_counteragents()

# logging.info(json.dumps(payload)
logging.info("=== counteragents ===")
# parsed = json.loads(dl.text.decode('utf-8'))
parsed = dl.text # .decode('utf-8')
print(dl.text.replace('\n', ''))
# logging.info(parsed)

"""
for dl_ca in counteragents_res:
   #logging.info(type(dl_ca))
   logging.info(dl_ca)
   logging.info("-----")
"""

logging.info('res_count={}'.format(1 + len(counteragents_res)))
# logging.info('text_count={}'.format(1 + len(json.loads(dl.text.decode('utf-8')))))

#logout
counteragents_res = dl.dl_logout()
