#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import time

from dl_app import DL_app

dl_contacts = DL_app('DL addrbook downloader')
dl_contacts.login(auth=True)

curs = dl_contacts.db_login()
curs = dl_contacts.conn.cursor()

addr_sql = """
SELECT id FROM shp.vw_dl_addresses WHERE 
(phones > 0 or contacts > 0) AND
"type" = 'delivery';
"""

curs.execute(addr_sql)
addr_id_list = []
addr_id_list = curs.fetchall()
# addr_id_list = curs.fetchmany(10)

csv = open('addr-phones-contacts.csv', 'w')
for addr_tuple in addr_id_list:
    addr_id = addr_tuple[0]

    dl_res = dl_contacts.dl.dl_book_address(addr_id)
    if 200 == dl_contacts.dl.status_code:
        logging.info('{} completed'.format(addr_id))
        csv.write('{}^"{}"\n'.format(addr_id, json.dumps(dl_res, ensure_ascii=False).replace('"', '""')))
    else:
        logging.warning('download contacts for add_id={} failed with status_code={}, text={}'.format(
            addr_id, dl_contacts.dl.status_code, dl_contacts.dl.text))
    time.sleep(4)

csv.close()
dl_contacts.dl.dl_logout()

# \copy shp.dl_addr_contacts_json(addr_id, jb) from 'addr-phones-contacts.csv' with (format csv, delimiter '^');
