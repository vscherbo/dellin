#!/usr/bin/env python3

""" Inquire order info from dellin
"""

#import json
import dataclasses
import datetime
import logging

import log_app
from pg_app import PGapp

import dl_app

#import sys



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

#dl_app.parser.add_argument('--doc_id', type=str, required=True, help='tracking number')
#dl_app.parser.add_argument('--shp_id', type=int, required=True, help='shp_id')

@dataclasses.dataclass
class Member:
    """ DL member's params """
    ca_id: int
    addr_id: int
    contact_ids: []
    phones_ids: []

@dataclasses.dataclass
class ReqParams:
    """ DL request's params """
    sender: Member
    receiver: Member
    boxes: int
    wepay: bool
    pre_shipdate: datetime.date
    delivery_type: int
    is_terminal: bool

class DLreq(dl_app.DL_app, log_app.LogApp):
    """ Class for requests v2 """

    def __init__(self, args, description):
        print('init1::', args)
        log_app.LogApp.__init__(self, args=args, description=description)
        print('init2::', args)
        dl_app.DL_app.__init__(self, args=args, description=description)
        print('init3::', args)
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
            contact_ids=[],
            phones_ids=[]
            )
        loc_receiver = Member(
            ca_id=rec["rcv_ca_id"],
            addr_id=rec["rcv_addr_id"],
            contact_ids=[],
            phones_ids=[]
            )
        self._req_params = ReqParams(
            sender=loc_sender,
            receiver=loc_receiver,
            wepay=False,
            boxes=1,
            pre_shipdate=None,
            delivery_type=None,
            is_terminal=False
                )
        """
        self._req_params["sender_id"] = rec["snd_ca_id"]
        self._req_params["snd_addr_id"] = None
        self._req_params["rcv_ca_id"] = None
        self._req_params["rcv_addr_id"] = None
        self._req_params["boxes"] = None
        self._req_params["wepay"] = None
        self._req_params["pre_shipdate"] = None
        self._req_params["delivery_type"] = None
        self._req_params["is_terminal"] = None
        """

    def _sender(self):
        """ Sender """
        self.pgdb.curs_dict.callproc('dl_req2_member', (self.shp_id, 'sender',))
        rec = self.pgdb.curs_dict.fetchone()
        logging.info('rec=%s', rec)
        sender_id = rec["ca_id"]
        sender_contact_id = rec["contact_ids"]
        sender = {
            "counteragentID" : sender_id,
            "contactIDs": sender_contact_id,
            "phoneIDs": rec["phone_ids"]
        }
        logging.info(sender)
        return sender


    def req(self, shp_id):
        """ Do request v2 """
        self.shp_id = shp_id
        self._get_req_params()
        #self._sender()


def main():
    """ Just main """
    log_app.PARSER.add_argument('--shp_id', type=int, required=True, help='shp_id to do request')
    args = log_app.PARSER.parse_args()

    app = DLreq(args=args, description='DL request v2')
    logging.info("args=%s", args)
    app.req(args.shp_id)

    """
    if app.login(auth=True):
        #arg = [].append(args.doc_id)
        logging.info('args.shp_id=%s', args.shp_id)
        app.req(args.shp_id)
        params = {}
        dl_res = app.dl.dl_request_v2(params)
        if dl_res is None:
            logging.error("dl_request res is None")
        elif "errors" in dl_res.keys():
            logging.error("dl_request errors=%s", dl_res["errors"])
        elif app.dl.status_code == 200:
            pass
            #logging.debug('arrival=%s', json.dumps(dl_res["orders"][0]['arrival'],
            #logging.debug('dl_res["orders"]=%s', json.dumps(dl_res["orders"],
            #                                                ensure_ascii=False, indent=4))
        else:
            err_str = 'ERROR=%s', app.dl.err_msg
            logging.error(err_str)
            print(err_str, file=sys.stderr, end='', flush=True)

        app.logout()
    """

if __name__ == '__main__':
    main()
