#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# import os
# import sys

import dl_app

dl_app.parser.add_argument('--url', type=str, required=True, help='URL справочника на api.dellin.ru')
args = dl_app.parser.parse_args()

app = dl_app.DL_app(args=args, description='DL directory download')
logging.info("args={}".format(args))

if app.login(auth=True):
    dl_res = app.dl.dl_any(args.url)
    if 200 == app.dl.status_code:
        logging.info("dl_res={}".format(dl_res))
        print(dl_res['hash'])
        print(dl_res['url'])
        #print(dl.text)
    app.logout()
