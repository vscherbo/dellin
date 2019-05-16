#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DL tracking request.
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


args = dl_app.parser.parse_args()

app = dl_app.DL_app(args=args, description='DL tracking')
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
    curs.execute("SELECT * FROM shp.dl_preorders();")
    rows = curs.fetchall()
    for (shp_id, dl_dt, doc_id) in rows:
        # DEBUG
        arg_sender = None
        arg_receiver = None
        logging.info("query dellin for shp_id=%d, dl_dt=%s, doc_id=%s", shp_id, dl_dt, doc_id)
        tracker_res = app.dl.dl_tracker(doc_id=doc_id)
        #logging.debug('tracker_res=%s', tracker_res)

        if tracker_res is None:
            logging.error("dl_tracker res is None")
        elif "errors" in tracker_res.keys():
            logging.error("dl_tracker errors=%s", tracker_res["errors"])
        else:
            # logging.debug(dl.text)
            for dl_doc in tracker_res["documents"]:
                if dl_doc["document_type"] != 'shipping':
                    logging.debug('=== SKIP doc=%s', dl_doc)
                    continue
                tr_num = dl_doc["document_id"]
                doc_date = dl_doc["create_date"]
                sz_weight = None
                sz_volume = None
                shp_height = None
                shp_width = None
                shp_length = None
                osz_weight = None
                osz_volume = None
                """
                sz_weight = dl_doc["order"]["sizedWeight"]
                sz_volume = dl_doc["order"]["sizedVolume"]
                doc_date = dl_doc["order"]["docDate"].replace('T', ' ')
                shp_height = dl_doc["order"]["height"]
                shp_width = dl_doc["order"]["width"]
                shp_length = dl_doc["order"]["length"]
                osz_weight = dl_doc["order"]["oversizedWeight"]
                osz_volume = dl_doc["order"]["oversizedVolume"]
                """
                logging.debug('got tr_num=%s, doc_date=%s for shp_id=%d', tr_num, doc_date, shp_id)
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

    logging.info("SELECT shp.dl_trnum_update();")
    curs.execute("SELECT shp.dl_trnum_update();")
    app.conn.commit()
    app.conn.close()

    # logout
    app.logout()
