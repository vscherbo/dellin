#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
import json
from datetime import date
import dl_app

# dl_app.parser.add_argument('--addr_id', type=int, required=True, help='ca addr_id') 
# dl_app.parser.add_argument('--phone', type=str, required=True, help='phone number') 
args = dl_app.parser.parse_args()

app = dl_app.DL_app(args=args, description='DL req test')
logging.info("args={}".format(args))

# --------------------------------------------
# Request.Delivery.deliveryType
delivery_type = 'auto'  # small|letter
deliveryType = {
        "type": delivery_type,
        "payer": 'receiver'
        }

# Request.Delivery.Derival
produse_date = date.strftime(date.today(), '%Y-%m-%d')
terminal_derival = 1  # TODO set
delivery_derival = {
        "produceDate": produse_date,
        "variant": 'terminal',
        "payer": 'receiver',
        "terminalID": terminal_derival
        }

# Request.Delivery.Arrival
terminal_arrival = 74  # TODO set
delivery_arrival = {
        "variant": 'terminal',
        "payer": 'receiver',
        "terminalID": terminal_arrival
        }

# Request.Delivery
delivery = {
        "deliveryType": deliveryType,
        "derival": delivery_derival,
        "arrival": delivery_arrival
        }

# --------------------------------------------
our_uid = '5078588d-b3af-4140-9660-5251a2e79104'  # ТД ЭП
# TODO set real uid

# Request.Members.requester
members_requester = {
        "role": "sender",
        "uid": our_uid
        }

# Request.Members.Sender
sender_id = 6619266  # TODO set
sender_contact_id = 84292152  # TODO set
sender_phone_id = 90166933  # TODO set
sender = {
        "counteragentID" : sender_id,
        "contactIDs": sender_contact_id,
        # "name": "Щербо В.А.",
        "phoneIDs": sender_phone_id
        }

# Request.Members.Receiver
receiver_id = 573899  # TODO set
receiver_contact_id = 84253436  # TODO set
receiver_phone_id = 90121936  # TODO set
receiver = {
        "counteragentID" : receiver_id,
        "contactIDs": receiver_contact_id,
        "phoneIDs": receiver_phone_id
        }

# Request.Members.Third

third_id = 6619266  # TODO set
third_contact_id = 84292152  # TODO set
third_phone_id = 90166933  # TODO set
third = {
        "counteragentID" : third_id,
        "contactIDs": third_contact_id,
        "phoneIDs": third_phone_id
        }

# Request.Members
members = {
        "requester": members_requester,
        "sender": sender,
        "receiver": receiver,
        # "third": receiver
        "third": third
        }

# --------------------------------------------
# Request.Cargo
insurance_payer = "receiver"
insurance = {
        "statedValue": 0.0,
        "payer": insurance_payer,
        "term": False,  # no insurance
        }

# TODO set
cargo_length = 0.1 
cargo_width = 0.1
cargo_height = 0.1
cargo_weight = 0.5
cargo_totalVolume = 0.001
cargo_totalWeight = 0.5

cargo = {
        "quantity": 1,
        "length": cargo_length,
        "width": cargo_width,
        "height": cargo_height,
        "weight": cargo_weight,
        "totalVolume": cargo_totalVolume,
        "totalWeight": cargo_totalWeight,
        "insurance": insurance,
        "freightName": 'Приборы'
        }


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
        "cargo": cargo,
        "payment": payment
        }

loc_auth = True

app.login(auth=loc_auth)

dl_res = app.dl.dl_test_request(request)
logging.info('dl.text={}'.format(app.dl.text))
#logging.info('dl_res={}'.format(dl_res))
print(json.dumps(dl_res, ensure_ascii=False, indent=4))

if app.dl.session_id:
    app.logout()

