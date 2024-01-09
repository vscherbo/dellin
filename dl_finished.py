#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DL tracking request.
"""
from datetime import datetime
import logging
import argparse
import time
import json
import ssl
import smtplib
from email.mime.text import MIMEText
#from email.message import EmailMessage
#from email.header import Header
#from email.headerregistry import Address

#import psycopg2.extras

import dl_app

EMAIL_TO = "vscherbo@kipspb.ru"
#EMAIL_TO = "delivery-dl@kipspb.ru"


OUTSIDE_DELLIN = ("draft", "processing", "pickup", "waiting", "declined")

INS_ATOL_Q = """INSERT INTO cash.atol_rcpt_q(ext_id, q_dt, bill_no) VALUES(%s, %s, %s);"""

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

def send_email(arg_to, arg_subj, arg_msg):
    """Just send"""

    smtp_srv = "smtp.mail.ru"
    port = 465
    _from = 'no-reply@kipspb.ru'
    # subject = u'Расхождения в отправке  Деллин и предзаказе'

    msg = MIMEText(arg_msg, 'plain', 'utf-8')
    msg.set_charset("UTF-8")
    msg.add_header('language', 'ru')  # Content-Language: ru
    msg["From"] = _from
    logging.debug(arg_to)
    msg["To"] = arg_to
    """
    msg["To"] = (Address("Владимир Щербо", "vscherbo", "kipspb.ru"),
                 Address("Билли Бонс", "billushka", "mail.ru"))
    """
    msg["Subject"] = arg_subj

    ### DEBUG only
    logging.info('get_content_type=%s', msg.get_content_type())
    logging.info('get_content_charset=%s', msg.get_content_charset())
    logging.info('get_charset=%s', msg.get_charset())
    for key, val in msg.items():
        logging.info('key=%s, val=%s', key, val)
    ###

    ret_code = 0
    rcpt_refused = []
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_srv, port, context=context) as smtp_obj:
            smtp_obj.login('no-reply@kipspb.ru', 'Rkx2iXXcmrqK1E6Licdg')

            #smtp_obj.set_debuglevel(True)
            rcpt_refused = smtp_obj.send_message(msg)
            #smtp_obj.set_debuglevel(False)

    except smtplib.SMTPResponseException as exc:
        ret_code = exc.smtp_code
    except smtplib.SMTPException:
        ret_code = 18

    if rcpt_refused:
        ret_code = 19

    logging.info('ret_code=%s', ret_code)

ARGS = dl_app.parser.parse_args()

APP = dl_app.DL_app(args=ARGS, description='DL tracking')
logging.info("ARGS=%s", ARGS)

if APP.login(auth=True):
    APP.db_login()


    CURS = APP.conn.cursor()
    CURS.execute("SELECT * FROM shp.dl_prepaid();")
    ROWS = CURS.fetchall()
    #ROWS = [(16715, '2020-07-03', '20-00011304449')]
    #ROWS = [(16719, '2020-07-03', '18347033')]
    #ROWS = [(16799, '2020-07-06', '18378910')]
    # ROWS = [(16821, '2020-07-07', '18397474')] Москва Румянцево
    """
    ROWS = [(16807, '2020-07-10', '18388225'),
            (16792, '2020-07-07', '18385027'),
            (16751, '2020-07-07', '18384706'),
            (16806, '2020-07-07', '18388059'),
            (16787, '2020-07-07', '18384537'),
            (16796, '2020-07-07', '18383875'),
            (16821, '2020-07-07', '18397474')]
    """
    #ROWS = [(49333, '2023-11-17', '40059971')]
    #ROWS = [(49323, '2023-11-17', '40054461')]

    for (ext_id, bill_no, doc_id) in ROWS:
        loc_delay = 3
        arg_sender = None
        arg_receiver = None
        logging.info("sleep before next loop loc_delay=%s", loc_delay)
        time.sleep(loc_delay)
        logging.info("query dellin for ext_id=%d, bill_no=%s, doc_id=%s", ext_id, bill_no, doc_id)
        tracker_res = APP.dl.dl_tracker(doc_id=doc_id)
        #logging.debug('tracker_res=%s', json.dumps(tracker_res, ensure_ascii=False, indent=4))

        if tracker_res is None:
            logging.error("dl_tracker res is None")
        elif "errors" in tracker_res:
            logging.error("dl_tracker errors=%s", tracker_res["errors"])
        elif "state" in tracker_res:
            # logging.debug(APP.dl.text)
            if tracker_res['state'] in OUTSIDE_DELLIN:
                logging.debug('=== SKIP state=%s', tracker_res['state'])
                continue
            elif tracker_res['state'] == 'finished':
                #logging.info('fin_dt=%s', tracker_res['order_dates']['finish'])
                atol_cmd = CURS.mogrify(INS_ATOL_Q, (ext_id,\
                    tracker_res['order_dates']['finish'], bill_no))
                logging.info('atol_cmd=%s', atol_cmd)
                CURS.execute(atol_cmd)
                APP.conn.commit()
            else:
                logging.debug('=== just logging state=%s', tracker_res['state'])


            logging.info("got tracker_res. sleep loc_delay=%s", loc_delay)
            time.sleep(loc_delay)
        else:
            logging.warning("dl_tracker unexpected tracker_res=%s",
                            json.dumps(tracker_res, ensure_ascii=False, indent=4))


    APP.conn.commit()
    APP.conn.close()

    # logout
    APP.logout()
