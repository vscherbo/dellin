#!/usr/bin/env python3
"""
Добавление записи в справочник контрагентов Деловых линий (ДЛ)
по информации из БД arc_energo
"""

import logging
import sys
import dl_app


"""
1. ?Проверка отсутствия такого контрагента
2. Если отсутствует, выбор ОПФ из справочника ДЛ
3. Получение адресных данных из функции
   shp.dl_ca_addr_fields ( dadata.ru, ext.dl_places, ext.dl_streets)
4. Добавление контрагента в справочник ДЛ
5. Добавление в таблицу dl_counteragents со статусом 1
"""

ERR_REASON = {}
ERR_REASON['name'] = 'Название'
ERR_REASON['opf_dl'] = 'ОПФ по справочнику Деллин'
ERR_REASON['inn'] = 'ИНН'
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

    dl_app.parser.add_argument('--code', type=int, required=True,
                               help='arc_energo.Предприятия.Код')
    dl_app.parser.add_argument('--address', type=str, required=False,
                               help='Произвольный адрес')
    args = dl_app.parser.parse_args()

    app = dl_app.DL_app(args=args, description='DL contact add')
    logging.info("args=%s", args)

    app.login(auth=True)
    app.db_login()

    curs = app.conn.cursor()

    if args.address:
        addr_sql = "select * from shp.dl_ca_addr_fields({}, '{}')"
        curs.execute(addr_sql.format(args.code, args.address))
    else:
        addr_sql = "select * from shp.dl_ca_addr_fields({})"
        curs.execute(addr_sql.format(args.code))
    (ret_flag, ret_addr_kladr_street, ret_addr_house, ret_addr_block,
     ret_addr_flat, ret_street) = curs.fetchone()

    if ret_flag:
        sql_ent = """SELECT "Предприятия".opf_dl as opf_dl, \
"Предприятия".opf as opf_name, \
trim(replace("Предприятие", coalesce("Предприятия".opf, ''), '')) as ent_name,\
"ЮрНазвание" as legal_name, \
"ИНН" as inn FROM "Предприятия" WHERE "Код"={};""".format(args.code)
        curs.execute(sql_ent)
        (opf_dl, opf_name, name, legal_name, inn) = curs.fetchone()

        logging.info('app.l_book_counteragents_update(name={}, opf_dl={},\
opf_name={}, inn={}, \
kladr_street={}, street={}, house={}, building={}, \
flat={});'.format(name, opf_dl, opf_name, inn,
                  ret_addr_kladr_street, ret_street,
                  ret_addr_house, ret_addr_block,
                  ret_addr_flat))

        # if OK loc_status = 1
        loc_status = int(bool(opf_dl and name and inn
                              and ret_addr_kladr_street and ret_addr_house))

        ca_params_sql = curs.mogrify(u"INSERT INTO shp.dl_ca_params\
(arc_code, any_address,\
ca_name, legal_name, inn, opf_dl, opf_name, \
street_kladr, street, house, chk_result)\
VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                                     (int(args.code), args.address,
                                      name, legal_name, inn, opf_dl, opf_name,
                                      ret_addr_kladr_street,
                                      ret_street,
                                      ret_addr_house, loc_status))
        curs.execute(ca_params_sql)
        app.conn.commit()

        # do not call dellin api
        if loc_status != 1:
            err_params = []
            if name is None:
                err_params.append(ERR_REASON['name'])
            if opf_dl is None:
                err_params.append('{} (ЮрНазвание: {})'.format(
                    ERR_REASON['opf_dl'],
                    legal_name))
            if inn is None:
                err_params.append(ERR_REASON['inn'])
            if ret_addr_kladr_street is None:
                err_params.append('{} (улица: {})'.format(
                    ERR_REASON['street_kladr'],
                    ret_street))
            if ret_addr_house is None:
                err_params.append(ERR_REASON['house'])
            print(ca_params_error(err_params), file=sys.stderr, end='',
                  flush=True)
            return

        dl_res = app.dl.dl_book_counteragents_update(
            opf_dl, name, inn,
            street_kladr=ret_addr_kladr_street,
            house=ret_addr_house,
            building=ret_addr_block,
            structure=None,
            flat=ret_addr_flat)
        logging.info('dl_book_counteragents_update res=%s', dl_res)

        if app.dl.status_code == 200:
            if 'success' in dl_res:
                ret_ca_id = dl_res['success']['counteragentID']
                logging.info('state=%s, counteragentID=%s',
                             dl_res['success']['state'], ret_ca_id)
                print(ret_ca_id, end='', flush=True)
                # add lastUpdate=now()
                loc_sql = curs.mogrify(u"""INSERT INTO
     ext.dl_counteragents(id, inn, status)
     VALUES(%s,%s,%s) ON CONFLICT DO NOTHING;""", (ret_ca_id, inn, 1))
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
        err_str = 'Error in parsing address'
        logging.error(err_str)
        print(err_str, file=sys.stderr, end='', flush=True)

    app.logout()


if __name__ == '__main__':
    main()
