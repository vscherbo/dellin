#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
Test DL request v1
"""

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
    logging.info("args={}".format(args))

    # --------------------------------------------
    # Request.Members.Sender
    sender_id = 6619266  # TODO set
    sender_address_id = 24109121  # TODO set
    sender_contact_id = [84292152]  # TODO set
    sender_phone_id = [90166933]  # TODO set
    sender = collections.OrderedDict()
    sender["counteragentID"] = sender_id
    sender["addressID"] = sender_address_id
    sender["contacts"] = sender_contact_id
    sender["phones"] = sender_phone_id
    sender["worktimeStart"] = "00:00"
    sender["worktimeEnd"] = "23:59"

    # Request.Members.Receiver
    receiver_id = 573899  # TODO set
    receiver_address_id = 24136692  # TODO set
    receiver_contact_id = [84253436]  # TODO set
    receiver_phone_id = [90121936]  # TODO set
    receiver = collections.OrderedDict()
    receiver["counteragentID"] = receiver_id
    receiver["addressID"] = receiver_address_id
    receiver["contacts"] = receiver_contact_id
    receiver["phones"] = receiver_phone_id
    receiver["worktimeStart"] = "00:00"
    receiver["worktimeEnd"] = "23:59"
    """
    receiver = {
            "counteragentID" : receiver_id,
            "addressID": receiver_address_id,
            "contacts": receiver_contact_id,
            "phones": receiver_phone_id,
            "worktimeStart": "00:00",
            "worktimeEnd": "23:59"
            }
    """

    # --------------------------------------------
    # TODO set
    cargo_length = 1
    cargo_width = 1
    cargo_height = 1
    cargo_weight = 1
    cargo_total_volume = 2
    cargo_total_weight = 1

    # Request
    production_mode = False
    request = collections.OrderedDict()
    request["sender"] = sender
    request["receiver"] = receiver
    request["day"] = 11
    request["month"] = 12
    request["year"] = 2018
    request["totalWeight"] = cargo_total_weight
    request["totalVolume"] = cargo_total_volume
    request["quantity"] = 1
    request["maxLength"] = cargo_length
    request["maxWidth"] = cargo_width
    request["maxHeight"] = cargo_height
    request["maxWeight"] = cargo_weight
    #request["statedValue"] = 0
    #request["loadingType"] = 1
    request["whoIsPayer"] = 2
    request["primaryPayer"] = 2
    request["paymentType"] = 1
    request["name"] = "devices"
    #request["document"] = "document"
    request["deliveryType"] = 6
    #request["freight_uid"] = "0xab117f72d9de97b843ba5fd18cc2e858"
    request["inOrder"] = 0
    #request["name"] = "Приборы"
    #request["document"] = "доверенность"

    loc_auth = True

    app.login(auth=loc_auth)

    dl_res = app.dl.dl_request_v1(request)
    logging.info('dl.text={}'.format(app.dl.text))
    #logging.info('dl_res={}'.format(dl_res))
    print(json.dumps(dl_res, ensure_ascii=False, indent=4))

    if app.dl.session_id:
        app.logout()

if __name__ == '__main__':
    main()
