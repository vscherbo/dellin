#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
Test DL request v1
"""

import datetime
import logging
import json
# from datetime import date
import collections
import dl_app


def main():
    """
    Just main proc
    """
    # dl_app.parser.add_argument('--addr_id', type=int, required=True, help='ca addr_id')
    # dl_app.parser.add_argument('--phone', type=str, required=True, help='phone number')
    args = dl_app.parser.parse_args()

    app = dl_app.DL_app(args=args, description='DL req test')
    logging.info("args=%s", args)

    app.db_login()

    curs = app.conn.cursor()
    # curs.execute("SELECT * FROM shp.dl_req_shipments();")
    curs.execute("SELECT shp_id FROM shp.dl_preorder_params WHERE sts_code = 0;")
    rows = curs.fetchall()
    # DEBUG rows = [4397]
    for row in rows:
        shp_id = row[0]
        logging.info("shp_id=%d", shp_id)
        # curs.execute("SELECT * FROM shp.dl_req_params(%s);", (shp_id,))
        curs.callproc('shp.dl_req_params', [shp_id])
        (sender_id, sender_address_id, receiver_id, receiver_address_id, boxes) = curs.fetchone()

        curs.callproc('shp.dl_req_sender_contacts', [shp_id])
        sender_contact_ids = [r[0] for r in curs.fetchall()]
        logging.debug('sender_contacts=%s', sender_contact_ids)

        curs.callproc('shp.dl_req_sender_phones', [shp_id])
        sender_phone_ids = [r[0] for r in curs.fetchall()]
        logging.debug('sender_phones=%s', sender_phone_ids)

        curs.callproc('shp.dl_req_receiver_contacts', [shp_id])
        receiver_contact_ids = [r[0] for r in curs.fetchall()]
        logging.debug('receiver_contacts=%s', receiver_contact_ids)

        curs.callproc('shp.dl_req_receiver_phones', [shp_id])
        receiver_phone_ids = [r[0] for r in curs.fetchall()]
        logging.debug('receiver_phones=%s', receiver_phone_ids)

        sender = collections.OrderedDict()
        sender["counteragentID"] = sender_id
        sender["addressID"] = sender_address_id
        sender["contacts"] = sender_contact_ids
        sender["phones"] = sender_phone_ids
        sender["worktimeStart"] = "00:00"
        sender["worktimeEnd"] = "23:59"

        # Receiver
        receiver = collections.OrderedDict()
        receiver["counteragentID"] = receiver_id
        receiver["addressID"] = receiver_address_id
        receiver["contacts"] = receiver_contact_ids
        receiver["phones"] = receiver_phone_ids
        receiver["worktimeStart"] = "00:00"
        receiver["worktimeEnd"] = "23:59"

        # --------------------------------------------
        # TODO set
        cargo_length = 0.01
        cargo_width = 0.01
        cargo_height = 0.01
        cargo_weight = 1
        cargo_total_volume = 0.001
        cargo_total_weight = 1

        # Request
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        request = collections.OrderedDict()
        request["sender"] = sender
        request["receiver"] = receiver
        request["day"] = tomorrow_date.day
        request["month"] = tomorrow_date.month
        request["year"] = tomorrow_date.year
        request["totalWeight"] = cargo_total_weight
        request["totalVolume"] = cargo_total_volume
        request["quantity"] = boxes
        request["maxLength"] = cargo_length
        request["maxWidth"] = cargo_width
        request["maxHeight"] = cargo_height
        request["maxWeight"] = cargo_weight
        request["statedValue"] = 0.0
        request["whoIsPayer"] = 2
        request["primaryPayer"] = 2
        request["paymentType"] = 1
        request["deliveryType"] = 1
        request["freight_uid"] = "0xab117f72d9de97b843ba5fd18cc2e858"
        request["inOrder"] = 0

        loc_auth = True

        app.login(auth=loc_auth)

        dl_res = app.dl.dl_request_v1(request)
        logging.info('dl.text=%s', app.dl.text)
        #logging.info('dl_res={}'.format(dl_res))
        logging.info(json.dumps(dl_res, ensure_ascii=False, indent=4))
        now = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        dl_answer = dl_res["answer"]
        if dl_answer["state"] == 'success':
            upd_sql = curs.mogrify(u"""
            UPDATE shp.dl_preorder_params SET sts_code=%s, upddate=%s, ret_code=%s, ret_msg=NULL, req_id=%s, req_barcode=%s 
            WHERE shp_id=%s;""", (1, now, app.dl.status_code, dl_answer["requestID"], dl_answer["barcode"], shp_id))
        else:
            upd_sql = curs.mogrify(u"""
            UPDATE shp.dl_preorder_params SET sts_code=%s, upddate=%s, ret_code=%s, ret_msg=%s
            WHERE shp_id=%s;""", (9, now, app.dl.status_code, json.dumps(dl_answer, ensure_ascii=False), shp_id))

        logging.info(u"upd_sql=%s", upd_sql)
        curs.execute(upd_sql)
        app.conn.commit()


    if app.dl.session_id:
        app.logout()

if __name__ == '__main__':
    main()
