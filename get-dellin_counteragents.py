#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import argparse
import configparser

from shp_dellin import DellinAPI
# import psycopg2

log_format = '[%(filename)-21s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'

(prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
conf_file_name = "dl.conf"

parser = argparse.ArgumentParser(description='get Dellin-directory URL')
parser.add_argument('--conf', type=str, default=conf_file_name, help='conf file')
parser.add_argument('--log_to_file', type=str, default='stdout', help='log destination')
parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
args = parser.parse_args()

numeric_level = getattr(logging, args.log_level, None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % numeric_level)

if 'stdout' == args.log_to_file:
    logging.basicConfig(stream=sys.stdout, format=log_format, level=numeric_level)
else:
    logging.basicConfig(filename=args.log_to_file, format=log_format, level=numeric_level)


config = configparser.ConfigParser(allow_no_value=True)
config.read(args.conf)

ark_appkey = config['dl_login']['ark_appkey']
user = config['dl_login']['user']
pw = config['dl_login']['pw']

dl = DellinAPI(ark_appkey, user, pw)
logging.info("logged in sess_id={0}".format(dl.sessionID))


counteragents_res = dl.dl_book_counteragents()

# logging.info(json.dumps(payload)
logging.info("=== counteragents ===")
# parsed = json.loads(dl.text.decode('utf-8'))
parsed = dl.text # .decode('utf-8')
with open('res-counteragents.txt', 'w') as of:
    of.write(dl.text.replace('\n', ''))
#print(dl.text.replace('\n', ''))
# logging.info(parsed)

logging.info('res_count={}'.format(1 + len(counteragents_res)))
# logging.info('text_count={}'.format(1 + len(json.loads(dl.text.decode('utf-8')))))

#logout
counteragents_res = dl.dl_logout()
