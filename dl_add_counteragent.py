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
ERR_REASON['opf_dl'] = 'ОПФ (организационно-правовая форма) юр.лица по справочнику Деллин'
ERR_REASON['inn'] = 'ИНН'
ERR_REASON['street_kladr'] = 'код улицы юр. адреса по КЛАДР'
ERR_REASON['house'] = 'номер дома юр. адреса'
ERR_REASON['opf_none'] = 'ОПФ юр.лица по справочнику Деллин или произвольная ОПФ'


def ca_params_error(params):
    """
    returns error message for user
    """
    return 'Отсутствуют обязательные для Деллин значения: ' + '/'.join(params)


def main():
    """
    Just main proc
    """

    dl_app.parser.add_argument('--code', type=int, required=True,
                               help='arc_energo.Предприятия.Код')
    dl_app.parser.add_argument('--address', type=str, required=False,
                               help='Произвольный адрес')
    dl_app.parser.add_argument('--name', type=str, required=False,
                               help='Название контрагента без ОПФ')
    dl_app.parser.add_argument('--form_name', type=str, required=False,
                               help='название ОПФ')
    dl_app.parser.add_argument('--country_id', type=str, required=False,
                               help='UID страны')
    dl_app.parser.add_argument('--juridical', type=bool, required=False,
                               help='флаг юрлицо')
    args = dl_app.parser.parse_args()

    app = dl_app.DL_app(args=args, description='DL counteragent add')
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
     ret_addr_flat, ret_street, ret_street_type, ret_addr_city_code,
     ret_addr_city) = curs.fetchone()

    if not ret_flag:
        err_str = 'Ошибка при разборе адреса через dadata.ru: {}'.format(ret_addr_city)
        logging.error(err_str)
        print(err_str, file=sys.stderr, end='', flush=True)
    else:
        sql_ent = """SELECT "Предприятия".opf_dl as opf_dl, \
"Предприятия".opf as opf_name, \
trim(replace("Предприятие", coalesce("Предприятия".opf, ''), '')) as ent_name,\
"ЮрНазвание" as legal_name, \
"ИНН" as inn FROM "Предприятия" WHERE "Код"={};""".format(args.code)
        curs.execute(sql_ent)
        (opf_dl, opf_name, name, legal_name, inn) = curs.fetchone()

        logging.info('app.l_book_ca_update(name={}, opf_dl={},\
 opf_name={}, inn={},\
 city_kladr={}, kladr_street={}, street={}, street_type={},\
 house={}, building={},\
 flat={});'.format(name, opf_dl, opf_name, inn,
                   ret_addr_city_code,
                   ret_addr_kladr_street, ret_street, ret_street_type,
                   ret_addr_house, ret_addr_block,
                   ret_addr_flat))

        # if OK loc_status = 1
        # loc_status = int(bool(opf_dl and name and inn and ret_addr_house))
        loc_status = int(bool(name and inn))
                              # and ret_addr_house))
                              # and ret_addr_kladr_street and ret_addr_house))

        if not opf_dl:
            if args.form_name:
                custom_form = {}
                custom_form["formName"] = args.form_name
                name = args.name
                opf_name = args.form_name
                custom_form["countryUID"] = args.country_id
                custom_form["juridical"] = args.juridical
            else:
                loc_status = -1

        logging.info('dl_book_ca_update loc_status=%s', loc_status)

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
            if loc_status == -1:
                err_params.append(ERR_REASON['opf_none'])
            else:
                if name is None:
                    err_params.append(ERR_REASON['name'])
                if inn is None:
                    err_params.append(ERR_REASON['inn'])
                #if (ret_addr_kladr_street is not None) and (ret_addr_house is None):
                #    err_params.append(ERR_REASON['house'])

            if err_params:
                print(ca_params_error(err_params), file=sys.stderr, end='',
                      flush=True)
            return

        params = {}
        params["name"] = name
        params["inn"] = inn
        if opf_dl:
            params["form"] = opf_dl
        else:
            params["customForm"] = custom_form

        jur_address = {}
        jur_address["building"] = ret_addr_block
        jur_address["structure"] = None
        jur_address["flat"] = ret_addr_flat

        # обработка улицы без кода КЛАДР
        if ret_addr_kladr_street is None:
            custom_street = {}
            custom_street["code"] = ret_addr_city_code.ljust(25, '0')
            custom_street["street"] = ret_street_type or 'ул. Отсутствующая'
            jur_address["customStreet"] = custom_street
        else:
            jur_address["street"] = ret_addr_kladr_street

        if ret_addr_house:
            jur_address["house"] = ret_addr_house[:5]
        else:
            jur_address["house"] = '1'

        params["juridicalAddress"] = jur_address
        logging.info('dl_book_ca_update params=%s', params)

        dl_res = app.dl.dl_book_ca_update(params)

        logging.info('dl_book_ca_update res=%s', dl_res)

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


    app.logout()


if __name__ == '__main__':
    main()
