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

UID_SQL = """SELECT uid FROM ext.dl_our_ca WHERE inn=(SELECT inn FROM ext.dl_counteragents
WHERE id=%s);"""

TERM_ID_SQL = "SELECT terminal_id FROM shp.vw_dl_addresses WHERE id=%s;"

def err_formatter(arg_res):
    """ makes error string """
    err_list = []
    for err in arg_res["errors"]:
        err_list.append(f'{err["detail"]}: {err["fields"]}')

    err_str = '/'.join(err_list)
    return err_str


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
        uid_sql = self.pgdb.curs_dict.mogrify(UID_SQL, (rec["snd_ca_id"] ,))
        logging.info('uid_sql=%s', uid_sql)
        if self.pgdb.run_query(uid_sql, dict_mode=True) == 0:
            res_uid = self.pgdb.curs_dict.fetchone()
            if res_uid is None:
                logging.warning('None result for uid_sql=%s', uid_sql)
            else:
                logging.info('res_uid=%s', res_uid["uid"])
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
            delivery_type=rec["delivery_type"],  # TOD0 1, 4, 6 - auto, express, avia
            is_terminal=rec["is_terminal"],
            our_uid=res_uid["uid"]
                )

    def _get_ids(self, mode):
        """ Get ids IDs from DB """
        self.pgdb.curs_dict.callproc(self.pg_get_ids[mode], (self.shp_id,))
        res = self.pgdb.curs_dict.fetchall()
        logging.info('res=%s', res)
        loc_ids = []
        for rec in res:
            loc_ids.append(rec[0])
        logging.info('mode=%s, proc=%s, loc_ids=%s', mode, self.pg_get_ids[mode], loc_ids)
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
        else:
            delivery_arrival["variant"] = 'address'
            delivery_arrival["addressID"] = loc_addr_id
            delivery_arrival["time"] = {"worktimeStart": "07:00", "worktimeEnd": "20:00"}
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

    if app.login(auth=True):
        #arg = [].append(args.doc_id)
        logging.info('args.shp_id=%s', args.shp_id)
        dl_res = app.req(args.shp_id, args.test)
        if dl_res is None:
            logging.error("dl_request res is None")
        elif "errors" in dl_res.keys():
            logging.error("dl_request errors=%s", dl_res["errors"])
            # err_str = ','.join([dl_res["errors"][0]["detail"]] + dl_res["errors"][0]["fields"])
            err_str = err_formatter(dl_res)
            print(err_str, file=sys.stderr, end='', flush=True)
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

                upd_sql = app.pgdb.curs.mogrify("""
UPDATE shp.dl_preorder_params SET sts_code=%s, upddate=%s, ret_code=%s,
ret_msg=NULL, req_id=%s, req_barcode=%s
WHERE shp_id=%s;""", (loc_status, now, app.dl.status_code, dl_data["requestID"],
                      dl_data.get("barcode"), args.shp_id))
                print(f'{dl_data["requestID"]}@{dl_data["barcode"]}', end='', flush=True)
            else:
                upd_sql = app.pgdb.curs.mogrify("""
UPDATE shp.dl_preorder_params SET sts_code=%s, upddate=%s, ret_code=%s,
ret_msg=%s
WHERE shp_id=%s;""", (9, now, app.dl.status_code, json.dumps(dl_data, ensure_ascii=False),
    args.shp_id))

            logging.info("upd_sql=%s", upd_sql)
            app.pgdb.curs.execute(upd_sql)
            app.pgdb.conn.commit()

        else:
            err_str = 'ERROR=%s', app.dl.err_msg
            logging.error(err_str)
            print(err_str, file=sys.stderr, end='', flush=True)

        app.logout()

if __name__ == '__main__':
    main()
