#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
import sys
import dl_app

dl_app.parser.add_argument('--cas', nargs='+', type=int, required=False, help='ids list') 
dl_app.parser.add_argument('--addresses', nargs='+', type=int, required=False, help='ids list') 
dl_app.parser.add_argument('--phones', nargs='+', type=int, required=False, help='ids list') 
dl_app.parser.add_argument('--contacts', nargs='+', type=int, required=False, help='ids list') 
args = dl_app.parser.parse_args()

app = dl_app.DL_app(args=args, description='DL addr_book delete')
logging.info("args={}".format(args))


if app.login(auth=True):
    dl_res = app.dl.dl_book_delete(ca_list=args.cas,
            addr_list=args.addresses,
            phone_list=args.phones,
            contact_list=args.contacts)
    logging.info('dl_res={}'.format(dl_res))
    if 200 == app.dl.status_code:
        if 'deleted' in dl_res:
            logging.info('res={}'.format(dl_res["deleted"]))
        else:
            err_str = 'ERROR={}'.format(dl_res)
            logging.error(err_str)
            print(err_str, file=sys.stderr, end='', flush=True)
    else:
        err_str = 'ERROR={}'.format(app.dl.err_msg)
        logging.error(err_str)
        print(err_str, file=sys.stderr, end='', flush=True)

    app.logout()
