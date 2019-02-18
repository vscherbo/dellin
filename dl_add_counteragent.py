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
     ret_addr_flat) = curs.fetchone()

    if ret_flag:
        """
            with ent as (SELECT "Предприятия".opf as opf,
            trim(replace("Предприятие", "Предприятия".opf, '')) as ent_name,
            "ИНН" as inn FROM "Предприятия" WHERE "Код"={})
            select ol.uid, ent.ent_name, ent.inn from ent
            join shp.dl_opf_list ol on ent.opf = ol.opf_name
            and country_id = (select c.country_id from shp.dl_countries c
            where c.country_name = 'Россия');
        """
        sql_ent = """SELECT "Предприятия".opf_dl as opf, \
trim(replace("Предприятие", "Предприятия".opf, '')) as ent_name, \
"ИНН" as inn FROM "Предприятия" WHERE "Код"={};""".format(args.code)
        curs.execute(sql_ent)
        (opf, name, inn) = curs.fetchone()

        logging.info('app.l_book_counteragents_update(opf={}, name={}, inn={}, \
kladr_street={}, house={}, building={}, \
structure={}, flat={});'.format(opf, name, inn, ret_addr_kladr_street,
                                ret_addr_house, ret_addr_block, None,
                                ret_addr_flat))
        dl_res = app.dl.dl_book_counteragents_update(
            opf, name, inn,
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
