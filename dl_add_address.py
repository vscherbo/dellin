#!/usr/bin/env python3
"""
Добавление записи в справочник адресов доставки контрагентов Деловых линий (ДЛ)
по информации из БД arc_energo
"""

import logging
import sys
import dl_app


ERR_REASON = {}
ERR_REASON['street_kladr'] = 'код улицы юр. адреса по КЛАДР'
ERR_REASON['house'] = 'номер дома'


def ca_params_error(params):
    """
    returns error message for user
    """
    return 'Отсутствуют значения: ' + '/'.join(params)


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

    addr_sql = "select * from shp.dl_ca_addr_fields({}, '{}')"
    curs.execute(addr_sql.format(-1, args.address))
    (ret_flag, ret_addr_kladr_street, ret_addr_house, ret_addr_block,
     ret_addr_flat, ret_street, ret_street_type, ret_addr_city_code,
     ret_addr_city) = curs.fetchone()

    if ret_flag:
        logging.info('app.dl_address_add(ca_id={}, kladr_street={}, street={},\
 house={}, building={}, flat={});'.format(args.ca_id, ret_addr_kladr_street,
                                          ret_street, ret_addr_house,
                                          ret_addr_block, ret_addr_flat))


        # do not call dellin api
        if not ret_addr_house:
            err_params = []
            if ret_addr_house is None:
                err_params.append(ERR_REASON['house'])
            print(ca_params_error(err_params), file=sys.stderr, end='',
                  flush=True)
            return

        params = {}
        params["counteragentID"] = args.ca_id
        params["house"] = ret_addr_house[:5]
        params["building"] = ret_addr_block
        params["structure"] = None
        params["flat"] = ret_addr_flat
        if ret_addr_kladr_street:
            params["street"] = ret_addr_kladr_street
        else:
            custom_street = {}
            custom_street["code"] = ret_addr_city_code.ljust(25, '0')
            custom_street["street"] = ret_street_type or 'ул. Отсутствующая'
            params["customStreet"] = custom_street

        dl_res = app.dl.dl_any_address_add(params)

        logging.info('dl_address_add res=%s', dl_res)

        if app.dl.status_code == 200:
            if 'success' in dl_res:
                ret_address_id = dl_res['success']['addressID']
                logging.info('state=%s, addressID=%s',
                             dl_res['success']['state'], ret_address_id)
                print(ret_address_id, end='', flush=True)
                # add lastUpdate=now()
                loc_sql = curs.mogrify(u"INSERT INTO ext.dl_addresses(\
 ca_id, id, address, code, street, house, is_terminal, type, status)\
 VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)\
 ON CONFLICT DO NOTHING;", (args.ca_id, ret_address_id,
                            args.address, ret_addr_kladr_street,
                            ret_street, ret_addr_house, 'f', 'delivery', 1))
                logging.info(u"loc_sql=%s", loc_sql)
                curs.execute(loc_sql)
                app.conn.commit()
            else:
                err_str = 'ERROR={}'.format(dl_res)
                logging.error(err_str)
                print(err_str, file=sys.stderr, end='', flush=True)
        else:
            err_str = 'ERROR={}'.format(app.dl.err_msg)
            logging.error(err_str)
            print(err_str, file=sys.stderr, end='', flush=True)

    else:
        err_str = 'Ошибка разбора адреса: {}'. format(ret_addr_city)
        logging.error(err_str)
        print(err_str, file=sys.stderr, end='', flush=True)

    app.logout()


if __name__ == '__main__':
    main()
