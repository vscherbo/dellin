#!/usr/bin/env python3

""" Inquire order info from dellin
"""

import dataclasses
import json
import logging
import sys
from datetime import date, datetime

import log_app
from pg_app import PGapp

import dl_app

SQL = """ SELECT dl_counteragents.inn AS sender_inn, dl_counteragents_1.inn AS receiver_inn,
delivery.term_id AS terminal_id
FROM ((ext.dl_addresses AS dl_addresses_1
INNER JOIN (((ship_bills
INNER JOIN shipments ON ship_bills.shp_id = shipments.shp_id)
INNER JOIN delivery ON ship_bills.dlvrid = delivery.dlvr_id)
INNER JOIN ext.dl_addresses ON shipments.firm_addr_id = dl_addresses.id) ON dl_addresses_1.id = delivery.dlvr_addr_id)
INNER JOIN ext.dl_counteragents AS dl_counteragents_1 ON dl_addresses_1.ca_id = dl_counteragents_1.id)
INNER JOIN ext.dl_counteragents ON dl_addresses.ca_id = dl_counteragents.id
WHERE shipments.shp_id=%s;"""

INN_SQL = "SELECT inn FROM ext.dl_counteragents WHERE id=%s;"

TERM_ID_SQL = "SELECT terminal_id FROM shp.vw_dl_addresses WHERE id=%s;"

INN_TO_UID = {
'7802715214': 'B1BC6E79-1591-11E1-B592-02215ECC9D4B',
'7802731174': 'AC65DB70-9142-11E2-98F4-E61F13ED5CB9',
'7804431521': '8710c33e-4480-4e9f-ace2-69b3845676e1',
'7805345064': '5078588d-b3af-4140-9660-5251a2e79104',
'7805599407': '09D59E9F-5BE4-11E2-B398-0050569420A4',
'7805781663': 'ab5c3b1c-e27d-4f83-8d0f-e3df07452576',
'7805812449': 'd3e555ce-a21b-4a5a-8c23-7b517fef3054',
'7816316876': '569f5b62-9779-46f4-908a-abf470aa0a57',
#'7816316876': 'fe56ca78-d06e-489e-a5de-8f98885ac80b',
'7816676981': '20e9d75b-0ec3-450c-b5d3-8b5b93b23a4f'
        }

@dataclasses.dataclass
class Member:
    """ DL member's params """
    ca_id: int
    addr_id: int
    contact_ids: []
    phone_ids: []

@dataclasses.dataclass
class ReqParams:
    """ DL request's params """
    #sender: Member
    #receiver: Member
    members: {}
    boxes: int
    wepay: bool
    pre_shipdate: str
    delivery_type: int
    is_terminal: bool
    our_uid: str

class DLreq(dl_app.DL_app, log_app.LogApp):
    """ Class for requests v2 """
    pg_get_ids = {'sender_contact': 'shp.dl_req_sender_contacts',
                  'receiver_contact': 'shp.dl_req_receiver_contacts',
                  'sender_phone': 'shp.dl_req_sender_phones',
                  'receiver_phone': 'shp.dl_req_receiver_phones'
                  }
    delivery_payer = {True: 'sender', False: 'receiver'}  # wepay
    delivery_type = {1: "auto", 4: "express", 6: "avia"}  # v1 -> v2

    def __init__(self, args, description):
        log_app.LogApp.__init__(self, args=args, description=description)
        dl_app.DL_app.__init__(self, args=args, description=description)
        config_filename = args.conf
        self.get_config(config_filename)
        self.pgdb = PGapp(pg_host=self.config['PG']['pg_host'],
                          pg_user=self.config['PG']['pg_user'])
        if self.pgdb.pg_connect():
            self.pgdb.set_session(autocommit=True)
            #self.api = dl_app.DL_app(args)
        else:
            logging.error('No connect to PG')
            #raise f"Failed to login to {self.config['PG']['pg_host']}"
        self.shp_id = None
        #self._req_params = ReqParams()
        self._req_params = None

#sql_str = self.curs.mogrify(SQL, (shp_id,))

    def _get_req_params(self):
        """ Get req params from DB """
        self.pgdb.curs_dict.callproc('dl_req_params', (self.shp_id,))
        rec = self.pgdb.curs_dict.fetchone()
        logging.info('rec=%s', rec)
        loc_sender = Member(
            ca_id=rec["snd_ca_id"],
            addr_id=rec["snd_addr_id"],
            contact_ids=self._get_ids('sender_contact'),
            phone_ids=self._get_ids('sender_phone')
            )
        inn_sql = self.pgdb.curs_dict.mogrify(INN_SQL, (rec["snd_ca_id"] ,))
        logging.info('inn_sql=%s', inn_sql)
        if self.pgdb.run_query(inn_sql, dict_mode=True) == 0:
            res_inn = self.pgdb.curs_dict.fetchone()
            logging.info('res_inn=%s', res_inn["inn"])
        #
        loc_receiver = Member(
            ca_id=rec["rcv_ca_id"],
            addr_id=rec["rcv_addr_id"],
            contact_ids=self._get_ids('receiver_contact'),
            phone_ids=self._get_ids('receiver_phone')
            )
        self._req_params = ReqParams(
            #sender=loc_sender,
            #receiver=loc_receiver,
            members= {"sender": loc_sender, "receiver": loc_receiver},
            #members["sender"]=loc_sender,
            wepay=rec["wepay"],
            boxes=rec["boxes"],
            pre_shipdate=rec["pre_shipdate"],
            delivery_type=rec["delivery_type"],  # TODO 1, 4, 6 - auto, express, avia
            is_terminal=rec["is_terminal"],
            our_uid=INN_TO_UID[res_inn["inn"]]
                )

    def _get_ids(self, mode):
        """ Get ids IDs from DB """
        self.pgdb.curs_dict.callproc(self.pg_get_ids[mode], (self.shp_id,))
        res = self.pgdb.curs_dict.fetchall()
        logging.info('res=%s', res)
        loc_ids = []
        for rec in res:
            loc_ids.append(rec[0])
        logging.info('mode=%s, loc_ids=%s', mode, loc_ids)
        return loc_ids

    def _member(self, role):
        """ Member """
        member = {
            "counteragentID": self._req_params.members[role].ca_id,
            "contactIDs": self._req_params.members[role].contact_ids,
            "phoneIDs": self._req_params.members[role].phone_ids
        }
        logging.info('role=%s, member=%s', role, member)
        return member

    def _arrival(self):
        """ prepare 'arrival' for request """
        delivery_arrival = {}

        loc_addr_id = self._req_params.members['receiver'].addr_id
        if self._req_params.is_terminal:
            delivery_arrival["variant"] = 'terminal'
            self.pgdb.curs_dict.callproc('shp.dl_term_id', (loc_addr_id,))
            res_term = self.pgdb.curs_dict.fetchone()
            if res_term is not None:
                logging.info('res_term=%s', res_term[0])
                delivery_arrival["terminalID"] = res_term[0]
            """
            # SELECT terminal_id FROM shp.vw_dl_addresses WHERE id = 46729939
            term_sql = self.pgdb.curs_dict.mogrify(TERM_ID_SQL, (loc_addr_id ,))
            logging.info('term_sql=%s', term_sql)
            if self.pgdb.run_query(term_sql, dict_mode=True) == 0:
                res_term = self.pgdb.curs_dict.fetchone()
                logging.info('res_term=%s', res_term["terminal_id"])
                delivery_arrival["terminalID"] = res_term["terminal_id"]
            """
        else:
            delivery_arrival["variant"] = 'address'
            delivery_arrival["addressID"] = loc_addr_id
        return delivery_arrival

    def _derival(self):
        """ prepare 'derival' for request """
        delivery_derival = {}

        # "request.payment.primaryPayer"
        #delivery_derival["payer"] = self.delivery_payer[self._req_params.wepay]

        delivery_derival["produceDate"] = date.strftime(self._req_params.pre_shipdate, '%Y-%m-%d')
        delivery_derival["variant"] = 'terminal'
        #delivery_derival["terminalID"] = self._req_params.members['sender'].addr_id
        delivery_derival["terminalID"] = 1  # Парнас
        return delivery_derival

    def _delivery(self):
        """ prepare 'delivery' for request """
        delivery = {
                "deliveryType": {"type": self.delivery_type[self._req_params.delivery_type]},
                "derival": self._derival(),
                "arrival": self._arrival()
                }
        logging.info("delivery=%s", delivery)
        return delivery

    def _cargo(self):
        """ prepare 'cargo' for request """
        cargo = {}
        insurance = {
            "statedValue": 0.0,
            # "payer": insurance_payer,  == "request.payment.primaryPayer"
            "term": False,  # no insurance
        }

        cargo_length = 0.1
        cargo_width = 0.1
        cargo_height = 0.1
        cargo_weight = 0.5
        cargo_total_volume = 0.001
        cargo_total_weight = 0.5

        cargo = {
            "quantity": self._req_params.boxes,
            "length": cargo_length,
            "width": cargo_width,
            "height": cargo_height,
            "weight": cargo_weight,
            "totalVolume": cargo_total_volume,
            "totalWeight": cargo_total_weight,
            "insurance": insurance,
            "freight_uid": "0xbfff425683f453bb413cb1ddc65d155c"  # 'Комплектующие'
        }
        logging.info("cargo=%s", cargo)
        return cargo

    def _payment(self):
        """ prepare 'payment' for request """
        payment = {
            "type": 'noncash',
            "primaryPayer": self.delivery_payer[self._req_params.wepay]
        }
        logging.info("payment=%s", payment)
        return payment

    def _members(self):
        """ prepare 'members' for request """
        #our_uid = '5078588d-b3af-4140-9660-5251a2e79104'  # ТД ЭП

        # Request.Members.requester
        members_requester = {
            "role": "sender",
            "uid": self._req_params.our_uid
        }
        members = {
            "requester": members_requester,
            "sender": self._member('sender'),
            "receiver": self._member('receiver')
        }
        logging.info("members=%s", members)
        return members

    def req(self, shp_id, test_mode):
        """ Do request v2 """
        self.shp_id = shp_id
        self._get_req_params()
        request = {}
        if test_mode:
            request["inOrder"] = False  # NON production!
        else:
            request["inOrder"] = True

        request["delivery"] = self._delivery()
        request["members"] = self._members()
        request["cargo"] = self._cargo()
        request["payment"] = self._payment()
        return self.dl.dl_request_v2(request)

def main():
    """ Just main """
    log_app.PARSER.add_argument('--shp_id', type=int, required=True, help='shp_id to do request')
    log_app.PARSER.add_argument('--test', type=bool, default=False,
            help='If True, do request in the test mode')
    args = log_app.PARSER.parse_args()

    app = DLreq(args=args, description='DL request v2')
    logging.info("args=%s", args)
    """
    dl_res = app.req(args.shp_id)
    logging.info("dl_res=%s", dl_res)
    """
    if app.login(auth=True):
        #arg = [].append(args.doc_id)
        logging.info('args.shp_id=%s', args.shp_id)
        dl_res = app.req(args.shp_id, args.test)
        if dl_res is None:
            logging.error("dl_request res is None")
        elif "errors" in dl_res.keys():
            logging.error("dl_request errors=%s", dl_res["errors"])
        elif app.dl.status_code == 200:
            logging.debug('dl_res=%s', json.dumps(dl_res,
                                                            ensure_ascii=False, indent=4))
            now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            dl_data = dl_res["data"]
            if dl_data["state"] == 'success':
                if args.test:
                    loc_status = 2
                else:
                    loc_status = 1

                upd_sql = app.pgdb.curs.mogrify(u"""
UPDATE shp.dl_preorder_params SET sts_code=%s, upddate=%s, ret_code=%s,
ret_msg=NULL, req_id=%s, req_barcode=%s
WHERE shp_id=%s;""", (loc_status, now, app.dl.status_code, dl_data["requestID"],
                      dl_data["barcode"], args.shp_id))
                print(f'{dl_data["requestID"]}@{dl_data["barcode"]}', end='', flush=True)
            else:
                upd_sql = app.pgdb.curs.mogrify(u"""
UPDATE shp.dl_preorder_params SET sts_code=%s, upddate=%s, ret_code=%s,
ret_msg=%s
WHERE shp_id=%s;""", (9, now, app.dl.status_code, json.dumps(dl_data, ensure_ascii=False),
    args.shp_id))

            logging.info(u"upd_sql=%s", upd_sql)
            app.pgdb.curs.execute(upd_sql)
            app.pgdb.conn.commit()

        else:
            err_str = 'ERROR=%s', app.dl.err_msg
            logging.error(err_str)
            print(err_str, file=sys.stderr, end='', flush=True)

        app.logout()

if __name__ == '__main__':
    main()
