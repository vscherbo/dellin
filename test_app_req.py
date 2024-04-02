#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
    Dellin v2/request
"""


import json
import logging
from datetime import date

import dl_app

# dl_app.parser.add_argument('--addr_id', type=int, required=True, help='ca addr_id')
# dl_app.parser.add_argument('--phone', type=str, required=True, help='phone number')
args = dl_app.parser.parse_args()

app = dl_app.DL_app(args=args, description='DL req test')
logging.info("args=%s",args)

def ca_id_to_counteragent(arg_id):
    """
        convert id to json structure
    """
    return arg_id

# def address_id_to_address(arg_id):
#    pass

def contact_id_to_contact(arg_id):
    """
        convert id to json structure
    """
    return arg_id

def terminal_id_to_address(arg_id):
    """
        convert id to json structure
    """
    return arg_id

def phone_id_to_phone(arg_id):
    """
        convert id to json structure
    """
    return arg_id

def _derival():
    """ Prepare derival """
    # Request.Delivery.Derival
    produce_date = date.strftime(date.today(), '%Y-%m-%d')
    terminal_derival = 1  # TODO set
    delivery_derival = {
        "produceDate": produce_date,
        "variant": 'terminal',
        "payer": 'receiver',
        "terminalID": terminal_derival
    }
    return delivery_derival

def _arrival():
    """ Prepare derival """
    # Request.Delivery.Arrival
    terminal_arrival = 74  # TODO set
    delivery_arrival = {
        "variant": 'terminal',
        "payer": 'receiver',
        "terminalID": terminal_arrival
    }
    return delivery_arrival

def _sender():
    """ Prepare sender """
    # Request.Members.Sender
    sender_id = 6619266  # TODO set
    sender_contact_id = [87652393]  # TODO set
    sender_phone_id = [92944190]  # TODO set
    sender = {
        "counteragentID" : sender_id,
        "contactIDs": sender_contact_id,
        # "name": "Щербо В.А.",
        "phoneIDs": sender_phone_id
    }
    return sender

def _receiver():
    """ Prepare sender """
    # Request.Members.Receiver
    receiver_id = 573899  # TODO set
    receiver_contact_id = [84253436]  # TODO set
    receiver_phone_id = [90121936]  # TODO set
    receiver = {
        "counteragentID" : receiver_id,
        "contactIDs": receiver_contact_id,
        "phoneIDs": receiver_phone_id
    }
    return receiver


def _cargo():
    """ Prepare cargo """
    # TODO set
    # Request.Cargo
    insurance_payer = "receiver"
    insurance = {
        "statedValue": 0.0,
        "payer": insurance_payer,
        "term": False,  # no insurance
    }

    cargo_length = 0.1
    cargo_width = 0.1
    cargo_height = 0.1
    cargo_weight = 0.5
    cargo_total_volume = 0.001
    cargo_total_weight = 0.5

    cargo = {
        "quantity": 1,
        "length": cargo_length,
        "width": cargo_width,
        "height": cargo_height,
        "weight": cargo_weight,
        "totalVolume": cargo_total_volume,
        "totalWeight": cargo_total_weight,
        "insurance": insurance,
        "freight_uid": "0xab117f72d9de97b843ba5fd18cc2e858"  # 'Комплектующие'
    }
    return cargo

def main():
    """ Just main """

    # --------------------------------------------
    # Request.Delivery.deliveryType
    delivery_type = 'auto'  # small|letter
    delivery_type_dict = {
        "type": delivery_type,
    }

    # Request.Delivery
    delivery = {
        "deliveryType": delivery_type_dict,
        "derival": _derival(),
        "arrival": _arrival()
    }

    # --------------------------------------------
    our_uid = '5078588d-b3af-4140-9660-5251a2e79104'  # ТД ЭП
    # TODO set real uid

    # Request.Members.requester
    members_requester = {
        "role": "sender",
        "uid": our_uid
    }

    """
    # Request.Members.Third
    third_id = 6619266  # TODO set
    third_contact_id = [87652393]  # TODO set
    third_phone_id = [92944190]  # TODO set
    third = {
        "counteragentID" : third_id,
        "contactIDs": third_contact_id,
        "phoneIDs": third_phone_id
    }
    """

    # Request.Members
    members = {
        "requester": members_requester,
        "sender": _sender(),
        "receiver": _receiver(),
        # "third": receiver
        #"third": third
    }

    # --------------------------------------------
    # --------------------------------------------
    # Request.Payment
    payment_type = 'noncash'
    payment = {
        "type": payment_type,
        "primaryPayer": 'receiver',
    }

    # Request
    production_mode = False
    request = {
        "inOrder": production_mode,
        "delivery": delivery,
        "members": members,
        "cargo": _cargo(),
        "payment": payment
    }
    do_request(request)

def do_request(arg_request):
    """ Make v2 request """

    loc_auth = True

    app.login(auth=loc_auth)

    dl_res = app.dl.dl_test_request(arg_request)
    # проверить dl_res = app.dl.dl_request_v2(request)
    logging.info('dl.text=%s', app.dl.text)
    #logging.info('dl_res={}'.format(dl_res))
    print('dl_res dumps:')
    print(json.dumps(dl_res, ensure_ascii=False, indent=4))

    if app.dl.session_id:
        app.logout()


if __name__ == '__main__':
    main()
