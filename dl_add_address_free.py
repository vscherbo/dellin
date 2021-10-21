#!/usr/bin/env python3
"""
Добавление записи в справочник адресов доставки контрагентов Деловых линий (ДЛ)
по информации из БД arc_energo
"""

import logging
import sys
import json
import dl_app


def main():
    """
    Just main proc
    """

    dl_app.parser.add_argument('--ca_id', type=int, required=True,
                               help='id контрагента Деллин')
    dl_app.parser.add_argument('--address', type=str, required=True,
                               help='Произвольный адрес')
    args = dl_app.parser.parse_args()

    app = dl_app.DL_app(args=args, description='DL address add')
    logging.info("args=%s", args)

    app.login(auth=True)
    app.db_login()

    curs = app.conn.cursor()


    #params = {}
    #params["counteragentID"] = args.ca_id
    #params["search"] = args.address
    #dl_res = app.dl.dl_address_add_v2(params)
    dl_res = app.dl.dl_address_add_v2(args.ca_id, args.address.replace('№', ''))

    logging.info('dl_address_add res=%s', dl_res)

    if dl_res['metadata']['status'] == 200:
        ret_address_id = dl_res['data']['addressID']
        logging.info('op status=%s, data.state=%s, addressID=%s',
                     dl_res['metadata']['status'], dl_res['data']['state'], ret_address_id)
        print(ret_address_id, end='', flush=True)
        # add lastUpdate=now()
        loc_sql = curs.mogrify(u"INSERT INTO ext.dl_addresses(\
ca_id, id, address, is_terminal, type, status)\
VALUES(%s,%s,%s,%s,%s,%s)\
ON CONFLICT DO NOTHING;", (args.ca_id, ret_address_id,
                           args.address, 'f', 'delivery', 1))
        logging.info(u"loc_sql=%s", loc_sql)
        curs.execute(loc_sql)
        app.conn.commit()
    else:
        err_str = json.dumps(dl_res["errors"], ensure_ascii=False)
        logging.error(err_str)
        print(err_str, file=sys.stderr, end='', flush=True)

    app.logout()


if __name__ == '__main__':
    main()
