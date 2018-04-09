#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import psycopg2
import argparse
import time
import ConfigParser
import io
from shp_dellin import DellinAPI
import sys
from datetime import datetime


def valid_date(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


log_format = '[%(filename)-21s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'

(prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
conf_file_name = "dl.conf"

parser = argparse.ArgumentParser(description='get tracking numbers of Dellin')
parser.add_argument('--conf', type=str, default=conf_file_name, help='conf file')
parser.add_argument('--start_date',
                    help="The Start Date - format YYYY-MM-DD",
                    required=False,
                    default=datetime.strftime(datetime.today(), '%Y-%m-%d'),
                    type=valid_date)
parser.add_argument("--finish_date",
                    help="The Finish Date - format YYYY-MM-DD",
                    required=False,
                    type=valid_date)
parser.add_argument('--log_to_file', type=bool, default=False, help='log destination')
parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
args = parser.parse_args()

numeric_level = getattr(logging, args.log_level, None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % numeric_level)

if args.log_to_file:
    log_dir = ''
    log_file = log_dir + prg_name + ".log"
    logging.basicConfig(filename=log_file, format=log_format, level=numeric_level)
else:
    logging.basicConfig(stream=sys.stdout, format=log_format, level=numeric_level)

with open(args.conf) as f:
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(f.read()))

ark_appkey = config.get('dl_login', 'ark_appkey')
user = config.get('dl_login', 'user')
pw = config.get('dl_login', 'pw')

logging.debug("SELECT * FROM shp_dl_tn_query('{}');".format(args.start_date))

dl = DellinAPI(ark_appkey, user, pw)
logging.info("logged in sess_id={0}".format(dl.sessionID))

pg_srv = 'vm-pg.arc.world'
conn = psycopg2.connect("host='" + pg_srv + "' dbname='arc_energo' user='arc_energo'")  # password='XXXX' - .pgpass
# TODO check return code

shp_cmd_template = "INSERT INTO shp.vs_dl_tracking(tracking_code, shipment_dt, src_inn, dst_inn) " \
                   "VALUES(%s, %s, %s, %s) ON CONFLICT DO NOTHING;"

curs = conn.cursor()
# curs.execute("SELECT dl_dt,	dl_sender, dl_receiver FROM vw_dl_shipping ORDER BY dl_dt;")
curs.execute("SELECT * FROM shp_dl_tn_query('{}');".format(args.start_date))
rows = curs.fetchall()
for (dl_dt, arg_sender, arg_receiver) in rows:
    tracker_res = dl.dl_tracker_adv(sender=arg_sender, receiver=arg_receiver, date_start=dl_dt, date_end=dl_dt)

    # print json.dumps(payload)
    # print "=== tracker ==="
    if tracker_res is None:
        logging.error("dl_tracker_adv res is None")
    elif tracker_res["errormsg"] != "":
        logging.error("dl_tracker_adv errormsg={0}".format(tracker_res["errormsg"].encode('utf-8')))
        # OBSOLETE shp_cmd = curs.mogrify(shp_cmd_template, (None, None, 3))  # 3 - статус "ошибка"
        # curs.execute(shp_cmd)
    else:
        # logging.debug(dl.text)
        # logging.info(tracker_res["orders"]["tracker"][0]["order"]['docNumber'])
        for dl_order in tracker_res["orders"]["tracker"]:
            tn = dl_order["order"]["docNumber"]
            logging.debug('got order={}'.format(dl_order["order"]))
            shp_cmd = curs.mogrify(shp_cmd_template, (tn, dl_dt, arg_sender, arg_receiver))
            logging.info(shp_cmd)
            curs.execute(shp_cmd)
            conn.commit()

            """
            order_res = dl.dl_orders(tn)
            json_orders = order_res["orders"]
            if json_orders is not None and len(json_orders) > 0:
                for jo_line in json_orders:
                    print "doc={0} / {1} / {2} / {3}".format(jo_line["id"], jo_line["ordered_at"], jo_line["arrival"]["terminal_name"].encode('utf-8'), arg_receiver)
                    # shp_cmd = curs.mogrify(shp_cmd_template, (jo_line["id"], jo_line["ordered_at"], jo_line["arrival"]["terminal_name"].encode('utf-8'), arg_receiver, arg_sender))
                    # print shp_cmd
                    # curs.execute(shp_cmd)
                #print "type json_orders=", type(json_orders)
            else:
                logging.warning('No json_orders: json_orders={}, len(json_orders)={}'.format(
                    json_orders, len(json_orders)
                ))
            """
    time.sleep(1)

curs.execute("SELECT shp.dl_set_tracking();")
conn.commit()
conn.close()

# logout
tracker_res = dl.dl_logout()
logging.info("logout {}".format(dl.text))
