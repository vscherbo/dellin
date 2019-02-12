#!/usr/bin/env python3

# from __future__ import print_function
import logging
import sys
import dl_app


"""
Добавление записи в справочник контрагентов Деловых линий (ДЛ)
по информации из БД arc_energo

* Если отсутствует, выбор ОПФ из справочника ДЛ
* Добавление контрагента в справочник ДЛ
* Добавление в таблицу dl_counteragents со статусом 1
"""

dl_app.parser.add_argument('--pdoc_id',
                           type=int,
                           required=True,
                           help='shp.person_doc.pdoc_id')
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
dl_res = app.dl.dl_book_ca_person_update(params)
logging.info('dl_book_ca_person_update res=%s', dl_res)

if 200 == app.dl.status_code:
    if 'success' in dl_res:
        ret_ca_id = dl_res['success']['counteragentID']
        logging.info('state=%s, counteragentID=%s',
                     dl_res['success']['state'], ret_ca_id)
        print(ret_ca_id, end='', flush=True)
        loc_sql = curs.mogrify(u"""INSERT INTO ext.dl_counteragents(id, type,
                               status) VALUES(%s,%s,%s)
                               ON CONFLICT DO NOTHING;""",  # lastUpdate=now()
                               (ret_ca_id, 'private', 1))
        logging.info(u"loc_sql={}".format(loc_sql))
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
