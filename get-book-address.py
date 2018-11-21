#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import configparser
import argparse
import os
import sys
import json

from shp_dellin import DellinAPI


log_format = '[%(filename)-21s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'

(prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
conf_file_name = "dl.conf"

parser = argparse.ArgumentParser(description='get Dellin-directory URL')
parser.add_argument('--conf', type=str, default=conf_file_name, help='conf file')
parser.add_argument('--addr_id', type=int, required=True, help="counteragent's address id")
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

dl_res = dl.dl_book_address(args.addr_id)
if 200 == dl.status_code:
    #print('{}^{}'.format(args.addr_id, dl.text.replace('\n', '')))
    with open('addr_{}.csv'.format(args.addr_id), 'w') as csv:
        csv.write('{}^"{}"'.format(args.addr_id, json.dumps(dl_res, ensure_ascii=False).replace('"', '""')))

# \copy shp.dl_addr_contacts_json(addr_id, jb) from 'addr.csv' with (format csv, delimiter '^');
        
