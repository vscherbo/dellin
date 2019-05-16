#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# import os
import sys

import dl_app

args = dl_app.parser.parse_args()
ret_code = -1 

app = dl_app.DL_app(args=args, description='DL counteragents in JSON download')
logging.info("args={}".format(args))

if app.login(auth=True):
    dl_res = app.dl.dl_book_counteragents()
    if 200 == app.dl.status_code:
        logging.info('res_count={}'.format(len(dl_res)))
        with open('res-counteragents.txt', 'w') as of:
            of.write(app.dl.text.replace('\n', ''))
        ret_code = 0
        """
        load into PG with copy-dl-counteragents.sql
        """
    else:
        err_str = 'ERROR={}'.format(app.dl.err_msg)
        logging.error(err_str)
        ret_code = 1

    app.logout()
else:    
    ret_code = 1

sys.exit(ret_code)
