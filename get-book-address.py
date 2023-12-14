#!/usr/bin/env python3
""" Get CSV file with address info from Dellin
"""

import logging
import configparser
import argparse
#import os
import sys
import json

from shp_dellin import DellinAPI

LOG_FORMAT = '[%(filename)-21s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s \
| %(asctime)-15s | %(message)s'


def main():
    """ Just main """

    #(prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
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

    if args.log_to_file == 'stdout':
        logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT, level=numeric_level)
    else:
        logging.basicConfig(filename=args.log_to_file, format=LOG_FORMAT, level=numeric_level)


    config = configparser.ConfigParser(allow_no_value=True)
    config.read(args.conf)

    ark_appkey = config['dl_login']['ark_appkey']
    user = config['dl_login']['user']
    pwd = config['dl_login']['pw']
    try:
        wrk_dir = config['env']['wrk_dir']
    except (KeyError, configparser.NoOptionError):
        wrk_dir = '/opt/dellin'
        logging.warning('NoOption wrk_dir, using hardcoded value=%s', wrk_dir)

    dl_api = DellinAPI(ark_appkey, user, pwd)

    dl_res = dl_api.dl_book_address(args.addr_id)
    if dl_api.status_code == 200:
        logging.debug('dl_res=%s', json.dumps(dl_res, ensure_ascii=False))
        #print('{}^{}'.format(args.addr_id, dl.text.replace('\n', '')))
        try:
            with open('{}/addr_{}.csv'.format(wrk_dir, args.addr_id), 'w') as csv:
                logging.debug('csv file opened')
                try:
                    csv.write('{}^"{}"'.format(
                        args.addr_id,
                        json.dumps(dl_res, ensure_ascii=False).replace('"', '""')))
                except (IOError, OSError) as excp:
                    logging.error('Error with writing the file, excp=%s', excp)
                except Exception as excp:
                    logging.error('Other error with writing the file, excp=%s', excp)
        except (FileNotFoundError, PermissionError, OSError) as excp:
            logging.error('Error with opening the file, excp=%s', excp)
        except Exception as excp:
            logging.error('Other error with opening the file, excp=%s', excp)

    # \copy ext.dl_addr_contacts_json(addr_id, jb) from 'addr.csv' with (format csv, delimiter '^');


if __name__ == '__main__':
    main()
