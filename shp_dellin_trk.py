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

import psycopg2.extras

import dl_app

# EMAIL_TO = "vscherbo@kipspb.ru"
EMAIL_TO = "delivery-dl@kipspb.ru"

SHP_CMD_TEMPLATE = """INSERT INTO shp.vs_dl_tracking(\
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

OUTSIDE_DELLIN = ("draft", "processing", "pickup", "waiting", "declined")

PREORDER_SQL = """ SELECT dl_counteragents.inn AS sender_inn,
dl_counteragents_1.inn AS receiver_inn,
delivery.term_id AS terminal_id
FROM ((ext.dl_addresses AS dl_addresses_1
INNER JOIN (((ship_bills
INNER JOIN shipments ON ship_bills.shp_id = shipments.shp_id)
INNER JOIN delivery ON ship_bills.dlvrid = delivery.dlvr_id)
INNER JOIN ext.dl_addresses ON shipments.firm_addr_id = dl_addresses.id) ON dl_addresses_1.id = delivery.dlvr_addr_id)
INNER JOIN ext.dl_counteragents AS dl_counteragents_1 ON dl_addresses_1.ca_id = dl_counteragents_1.id)
INNER JOIN ext.dl_counteragents ON dl_addresses.ca_id = dl_counteragents.id
WHERE shipments.shp_id=%s LIMIT 1;"""

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

    smtp_srv = "smtp.yandex.ru"
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
            smtp_obj.login('no-reply@kipspb.ru', 'Never-adm1n')

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

ROLE_NAME = {'sender': 'отправителя', 'receiver': 'получателя'}
INN_SQL_TEMPL = 'SELECT name FROM ext.dl_counteragents WHERE inn=%s LIMIT 1;'
TERMINAL_SQL_TEMPL = 'SELECT name, address FROM shp.vw_dl_terminal WHERE id=%s LIMIT 1;'

def inn2name(arg_inn):
    """
        counteragent name by INN
        :arg_inn - INN of a counteragent
    """
    if arg_inn:
        curs_dict = APP.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        inn_sql = curs_dict.mogrify(INN_SQL_TEMPL, (arg_inn,))
        logging.info('inn_sql=%s', inn_sql)
        curs_dict.execute(inn_sql)
        res = curs_dict.fetchone()
        curs_dict.close()
        ret_val = res.get('name', 'Название по ИНН не найдено')
    else:
        ret_val = 'arg_inn is None'
    return ret_val

def inn_msg(dl_inn, pg_inn, arg_role):
    """ Make message about a differnece in INN
        :dl_inn - INN from dellin.ru
        :pg_inn - INN from PG (pre-order)
        :arg_role - sender or receiver
    """
    loc_msg = None
    if dl_inn != pg_inn:
        loc_msg = """ИНН {role_name}={dl_inn} {dl_name} в заказе Деллин отличается от ИНН
{role_name}={pg_inn} {pg_name} в предзаказе""".format(role_name=ROLE_NAME[arg_role],\
                                                      dl_inn=dl_inn,
                                                      dl_name=inn2name(dl_inn),
                                                      pg_inn=pg_inn,
                                                      pg_name=inn2name(pg_inn))
    return loc_msg

def terminal_name(arg_terminal):
    """ Returns Dellin terminal name by its ID
    """
    if not arg_terminal:
        return 'до двери'
    curs_dict = APP.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    terminal_sql = curs_dict.mogrify(TERMINAL_SQL_TEMPL, (arg_terminal,))
    logging.info('terminal_sql=%s', terminal_sql)
    curs_dict.execute(terminal_sql)
    res = curs_dict.fetchone()
    curs_dict.close()
    return '{}, {}'.format(res.get('name', 'Название терминала по id не найдено'),
                           res.get('address', 'Адрес терминала по id не найден'))

def terminal_msg(dl_id, pg_id, arrival_address):
    """ Make message about a differnece in INN
        :dl_id - terminal_id from dellin.ru
        :pg_id - terminal_id from PG (pre-order)
    """
    loc_msg = None
    if dl_id is None and pg_id is None:
        pass
    elif arrival_address and pg_id is None:
        pass
    elif dl_id != pg_id:
        loc_msg = """Терминал в заказе Деллин:
{dl_term_name}
отличается от терминала в предзаказе:
{pg_term_name}
""".format(dl_term_name=terminal_name(dl_id), pg_term_name=terminal_name(pg_id))
    return loc_msg

def verify_order(arg_doc_id, arg_tr_num, arg_shp_id):
    """ Inquire order info from dellin
    """
    dl_res = APP.dl.dl_orders_v3(arg_tr_num)
    if dl_res is None:
        logging.error("dl_orders res is None")
    elif "errors" in dl_res.keys():
        logging.error("dl_orders errors=%s", dl_res["errors"])
    elif APP.dl.status_code == 200:
        logging.debug('arrival=%s', json.dumps(dl_res["orders"][0]['arrival'],
                                               ensure_ascii=False, indent=4))
        # for SQL print(dl_res["orders"][0], file=sys.stdout, end='', flush=True)
        sender_inn = dl_res["orders"][0]['sender'].get('inn', 'empty')
        receiver_inn = dl_res["orders"][0]['receiver'].get('inn', 'empty')
        terminal_id = dl_res["orders"][0]['arrival'].get('terminalId', 'empty')
        arrival_addr = dl_res["orders"][0]['arrival'].get('address', 'empty')
        logging.info('sender_inn=%s, receiver_inn=%s, terminal_id=%s',
                     sender_inn, receiver_inn, terminal_id)

        curs_dict = APP.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql_str = curs_dict.mogrify(PREORDER_SQL, (arg_shp_id,))
        logging.info('sql_str=%s', sql_str)
        curs_dict.execute(sql_str)
        rec = curs_dict.fetchone()
        curs_dict.close()
        if not rec:
            logging.warning('PREORDER_SQL returns NULL shp_id=%s', arg_shp_id)
        else:
            pg_sender_inn = rec['sender_inn']
            pg_receiver_inn = rec['receiver_inn']
            pg_terminal_id = rec['terminal_id']
            logging.info('pg_sender_inn=%s, pg_receiver_inn=%s, pg_terminal_id=%s',
                         pg_sender_inn, pg_receiver_inn, pg_terminal_id)

            body = ""
            warns = []
            loc_str = inn_msg(sender_inn, pg_sender_inn, 'sender')
            if loc_str:
                warns.append(loc_str)

            loc_str = inn_msg(receiver_inn, pg_receiver_inn, 'receiver')
            if loc_str:
                warns.append(loc_str)

            loc_str = terminal_msg(terminal_id, pg_terminal_id, arrival_addr)
            """ useless
            if loc_str:
                warns.append(loc_str)
            """

            if warns:
                warns.insert(0, """Выявлены расхождения в отправке (shp_id={})
    между предзаказом {} и фактическим заказом Деллин {}:
    """.format(arg_shp_id, arg_doc_id, arg_tr_num))
                body = u'\r\n'.join(warns)
                subj = u'Расхождения между отправкой Деллин {tr_num} \
    и предзаказом {pre_order}'.format(tr_num=arg_tr_num, pre_order=arg_doc_id)
                logging.info('body=%s', body)
                to_addr = EMAIL_TO
                msg = """{_body}
    Почтовый робот 'АРК Энергосервис'"""
                send_email(to_addr, subj, msg.format(_body=body))


ARGS = dl_app.parser.parse_args()

APP = dl_app.DL_app(args=ARGS, description='DL tracking')
logging.info("ARGS=%s", ARGS)

if APP.login(auth=True):
    APP.db_login()


    CURS = APP.conn.cursor()
    CURS.execute("SELECT * FROM shp.dl_preorders();")
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
    #ROWS = [(19795, '2020-11-09', '20009486')]

    for (shp_id, dl_dt, doc_id) in ROWS:
        loc_delay = 3
        arg_sender = None
        arg_receiver = None
        logging.info("query dellin for shp_id=%d, dl_dt=%s, doc_id=%s", shp_id, dl_dt, doc_id)
        tracker_res = APP.dl.dl_tracker(doc_id=doc_id)
        #logging.debug('tracker_res=%s', json.dumps(tracker_res, ensure_ascii=False, indent=4))

        if tracker_res is None:
            logging.error("dl_tracker res is None")
        elif "errors" in tracker_res.keys():
            logging.error("dl_tracker errors=%s", tracker_res["errors"])
        else:
            # logging.debug(APP.dl.text)
            if tracker_res['state'] in OUTSIDE_DELLIN:
                logging.debug('=== SKIP state=%s', tracker_res['state'])
                continue
            loc_shipping_doc = None
            loc_request_doc = None
            loc_shipping_date = None
            loc_request_date = None
            for dl_doc in tracker_res["documents"]:
                if dl_doc["document_type"] == 'shipping':
                    loc_shipping_doc = dl_doc["document_id"]
                    loc_shipping_date = dl_doc["create_date"]
                elif dl_doc["document_type"] == 'request' and dl_doc["state"] == "processed":
                    loc_request_doc = dl_doc["document_id"]
                    loc_request_date = dl_doc["produce_date"]
                else:
                    logging.debug('=== SKIP doc=%s', dl_doc)
                    continue
            tr_num = loc_shipping_doc or loc_request_doc
            doc_date = loc_shipping_date or loc_request_date
            if tr_num:
                # short delay if found
                loc_delay = 1
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
                shp_cmd = CURS.mogrify(SHP_CMD_TEMPLATE,
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
                CURS.execute(shp_cmd)
                APP.conn.commit()

                time.sleep(loc_delay + 4)
                verify_order(doc_id, tr_num, shp_id)

        time.sleep(loc_delay)

    logging.info("SELECT shp.dl_trnum_update();")
    CURS.execute("SELECT shp.dl_trnum_update();")
    APP.conn.commit()
    APP.conn.close()

    # logout
    APP.logout()
