#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced DL tracking request.
"""
from datetime import datetime
import logging
import argparse
import time

import dl_app

def valid_date(date_str):
    """
    DL date validation
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date_str)
        raise argparse.ArgumentTypeError(msg)

dl_app.parser.add_argument('--start_date',
                           help="The Start Date - format YYYY-MM-DD",
                           required=False,
                           default=datetime.strftime(datetime.today(), '%Y-%m-%d'),
                           type=valid_date)
dl_app.parser.add_argument("--finish_date",
                           help="The Finish Date - format YYYY-MM-DD",
                           required=False,
                           type=valid_date)

args = dl_app.parser.parse_args()

app = dl_app.DL_app(args=args, description='DL advanced tracking')
logging.info("args={}".format(args))

if app.login(auth=True):
    app.db_login()

    shp_cmd_template = """INSERT INTO shp.vs_dl_tracking(\
tracking_code,\
shp_id,\
shipment_dt,\
src_inn,\
dst_inn,\
sized_weight,\
sized_volume,\
shp_height,\
shp_width,\
shp_length,\
oversized_weight,\
oversized_volume,\
doc_date)\
 VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\
 ON CONFLICT DO NOTHING;"""

    curs = app.conn.cursor()
    # curs.execute("SELECT * FROM shp_dl_tn_query('{}');".format(
    curs.execute("SELECT * FROM shp.dl_trnum_query('{}');".format(
        args.start_date))
    rows = curs.fetchall()
    for (shp_id, arg_sender, arg_receiver, dl_dt) in rows:
        logging.info("query dellin for sender={}, \
                      receiver={} \
                      date_start={} \
                      date_end={}". format(arg_sender, arg_receiver,
                                           dl_dt, dl_dt))
        tracker_res = app.dl.dl_tracker_adv(sender=arg_sender,
                                            receiver=arg_receiver,
                                            date_start=dl_dt,
                                            date_end=dl_dt)

        if tracker_res is None:
            logging.error("dl_tracker_adv res is None")
        elif tracker_res["errormsg"] != "":
            logging.error("dl_tracker_adv errormsg={}".format(tracker_res["errormsg"]))
        else:
            # logging.debug(dl.text)
            # logging.info(tracker_res["orders"]["tracker"][0]["order"]['docNumber'])
            for dl_order in tracker_res["orders"]["tracker"]:
                tr_num = dl_order["order"]["docNumber"]
                sz_weight = dl_order["order"]["sizedWeight"]
                sz_volume = dl_order["order"]["sizedVolume"]
                doc_date = dl_order["order"]["docDate"].replace('T', ' ')
                shp_height = dl_order["order"]["height"]
                shp_width = dl_order["order"]["width"]
                shp_length = dl_order["order"]["length"]
                osz_weight = dl_order["order"]["oversizedWeight"]
                osz_volume = dl_order["order"]["oversizedVolume"]
                logging.debug('got order={} for shp_id={}'.format(dl_order["order"], shp_id))
                shp_cmd = curs.mogrify(shp_cmd_template,
                                       (tr_num,
                                        shp_id,\
                                        dl_dt,\
                                        arg_sender,\
                                        arg_receiver,\
                                        sz_weight,\
                                        sz_volume,\
                                        shp_height,\
                                        shp_width,\
                                        shp_length,\
                                        osz_weight,\
                                        osz_volume,\
                                        doc_date
                                       ))
                logging.info(shp_cmd)
                curs.execute(shp_cmd)
                app.conn.commit()

        time.sleep(1)

    # logging.info("SELECT shp.dl_set_tracking();")
    # curs.execute("SELECT shp.dl_set_tracking();")
    logging.info("SELECT shp.dl_trnum_update();")
    curs.execute("SELECT shp.dl_trnum_update();")
    app.conn.commit()
    app.conn.close()

    # logout
    app.logout()
