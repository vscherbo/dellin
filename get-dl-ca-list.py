#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# import os
import sys

import dl_app

dl_app.parser.add_argument('--ca_ids', nargs='+', required=True, help="counteragents id list")
args = dl_app.parser.parse_args()
ret_code = -1 

app = dl_app.DL_app(args=args, description='DL counteragents in JSON download')
logging.info("args={}".format(args))
logging.info("type(args.ca_ids)={}".format(type(args.ca_ids)))

if app.login(auth=True):
    dl_res = app.dl.dl_book_counteragents_list(args.ca_ids)
    if 200 == app.dl.status_code:
        logging.info('res_count={}'.format(len(dl_res)))
        with open('res-counteragents-v2.txt', 'w') as of:
            of.write(app.dl.text.replace('\n', '').replace('\\', '\\\\'))
        ret_code = 0
        """
        load into PG with inc-dl-counteragents-v2.sql
        """
    else:
        err_str = 'ERROR={}'.format(app.dl.err_msg)
        logging.error(err_str)
        ret_code = 1

    app.logout()
else:    
    ret_code = 1

sys.exit(ret_code)
