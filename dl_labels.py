#!/usr/bin/env python
""" DL labels
"""
# import argparse
# import configparser
#from dl_app import DL_app
import base64
import logging

import dl_app

dl_app.parser.add_argument('--req_id', type=int, required=True, help='DL tracking number')
args = dl_app.parser.parse_args()


dl_labels = dl_app.DL_app(args=args, description='DL labels')
logging.info("args=%s", args)
dl_labels.login(auth=True)


dl_res = dl_labels.dl.dl_get_labels(args.req_id)
if dl_res['metadata']['status'] == 200 and dl_res['state'] == 'processed':
    filename = f'{args.req_id}.pdf'
    with open(filename, "wb") as barcode_output:
        try:
            content = base64.b64decode(dl_res["data"][0]["base64"])
            barcode_output.write(content)
        except (IndexError, AttributeError):
            logging.error('dl_res=%s', dl_res)
            logging.error('err=%s', dl_labels.dl.err_msg)


logging.info('dl_res=%s', dl_res)

dl_labels.dl.dl_logout()
