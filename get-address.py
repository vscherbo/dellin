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
parser.add_argument('--ca_id', type=int, required=True, help="counteragent id")
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

dl_res = dl.dl_addresses(args.ca_id)
if 200 == dl.status_code:
    #print('{}^{}'.format(args.ca_id, dl.text.replace('\n', '')))
    with open('ca_{}_addr.csv'.format(args.ca_id), 'w') as csv:
        csv.write('{}^"{}"'.format(args.ca_id, json.dumps(dl_res, ensure_ascii=False).replace('"', '""')))
else:
    sys.exit(2)

# \copy ext.dl_addresses_json(ca_id, jb) from 'ca_9999999_addr.csv' with (format csv, delimiter '^');

