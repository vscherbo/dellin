#!/usr/bin/env python3
"""
Добавление частного лица в справочник контрагентов Деловых линий (ДЛ)
из БД arc_energo
"""

# from __future__ import print_function
import logging
import sys
import dl_app


"""
Добавление записи в справочник контрагентов Деловых линий (ДЛ)
по информации из БД arc_energo

* Добавление контрагента в справочник ДЛ
* Добавление в таблицу dl_counteragents со статусом 1
"""
ERR_REASON = {}
ERR_REASON['name'] = 'ФИО'
ERR_REASON['doc_prenum'] = 'серия документа'
ERR_REASON['doc_number'] = 'номер документа'


def ca_params_error(params):
    """
    returns error message for user
    """
    return 'Отсутствуют значения: ' + '/'.join(params)


def check_params(person_name, doc_prenum, doc_num):
    """
    check required params
    """
    # if OK loc_status = 1
    loc_ok = bool(person_name and doc_prenum and doc_num)

    # do not call dellin api
    if not loc_ok:
        err_params = []
        if person_name is None:
            err_params.append(ERR_REASON['name'])
        if doc_prenum is None:
            err_params.append(ERR_REASON['doc_prenum'])
        if doc_num is None:
            err_params.append(ERR_REASON['doc_number'])
        print(ca_params_error(err_params), file=sys.stderr, end='',
              flush=True)

    return loc_ok


def main():
    """
    Just main proc
    """

    dl_app.parser.add_argument('--pdoc_id',
                               type=int,
                               required=True,
                               help='arc_energo.person_doc.pdoc_id')
    args = dl_app.parser.parse_args()

    app = dl_app.DL_app(args=args, description='DL person add')
    logging.info("args=%s", args)

    app.login(auth=True)
    app.db_login()

    curs = app.conn.cursor()

    person_docs = ('unknown', 'passport', 'drivingLicence', 'foreignPassport')

    sql_doc = """
        SELECT doc_type, doc_prenum, doc_num, doc_issue::varchar, e."ФИО"
        FROM person_doc
        join "Работники" e on e."КодРаботника" = emp_code
        WHERE pdoc_id={};
        """.format(args.pdoc_id)
    curs.execute(sql_doc)
    (doc_type, doc_prenum, doc_num, doc_issue, person_name) = curs.fetchone()
    params = {}
    params["form"] = '0xAB91FEEA04F6D4AD48DF42161B6C2E7A'
    params["name"] = person_name
    doc = {}
    doc["type"] = person_docs[doc_type]
    doc["serial"] = doc_prenum
    doc["number"] = doc_num
    doc["date"] = doc_issue
    params["document"] = doc

    logging.info('dl_book_ca_person_update(doc_type=%s, doc_prenum=%s, doc_num=%s,\
                  doc_issue=%s, person_name=%s)',
                 doc_type, doc_prenum, doc_num, doc_issue, person_name)

    # do not call dellin api
    if not check_params(person_name, doc_prenum, doc_num):
        return

    dl_res = app.dl.dl_book_ca_person_update(params)
    logging.info('dl_book_ca_person_update res=%s', dl_res)

    if app.dl.status_code == 200:
        if 'success' in dl_res:
            ret_ca_id = dl_res['success']['counteragentID']
            logging.info('state=%s, counteragentID=%s',
                         dl_res['success']['state'], ret_ca_id)
            print(ret_ca_id, end='', flush=True)
            loc_sql = curs.mogrify(u"""INSERT INTO ext.dl_counteragents(id, type,
                                   status) VALUES(%s,%s,%s)
                                   ON CONFLICT DO NOTHING;""",
                                   (ret_ca_id, 'private', 1))
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
