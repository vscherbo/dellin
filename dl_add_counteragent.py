#!/usr/bin/env python3

import os
import logging
import psycopg2
import argparse
import configparser
from shp_dellin import DellinAPI
import sys


"""
Добавление записи в справочник контрагентов Деловых линий (ДЛ)
по информации из БД arc_energo

1. ?Проверка отсутствия такого контрагента
2. Если отсутствует, выбор ОПФ из справочника ДЛ
3. Получение адресных данных из dadata.ru, shp.dl_places, shp.dl_streets
4. 
5. 
"""

log_format = '[%(filename)-21s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'

(prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
conf_file_name = "dl.conf"

parser = argparse.ArgumentParser(description='add counteragent to address book of Dellin')
parser.add_argument('--conf', type=str, default=conf_file_name, help='conf file')
parser.add_argument('--pg_srv', type=str, default='vm-pg-devel.arc.world', help='PG hostname')
parser.add_argument('--code', type=int, help='arc_energo.Предприятия.Код')
parser.add_argument('--log_to_file', type=bool, default=False, help='log destination')
parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
args = parser.parse_args()

numeric_level = getattr(logging, args.log_level, None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % numeric_level)

if args.log_to_file:
    log_dir = ''
    log_file = log_dir + prg_name + ".log"
    logging.basicConfig(filename=log_file, format=log_format, level=numeric_level)
else:
    logging.basicConfig(stream=sys.stdout, format=log_format, level=numeric_level)


config = configparser.ConfigParser(allow_no_value=True)
config.read(args.conf)
API_KEY = config['dadata_login']['API_KEY']

ark_appkey = config['dl_login']['ark_appkey']
user = config['dl_login']['user']
pw = config['dl_login']['pw']

conn = psycopg2.connect("host='" + args.pg_srv + "' dbname='arc_energo' user='arc_energo'")  # password='XXXX' - .pgpass
# TODO check return code

curs = conn.cursor()

addr_sql = """
WITH dd AS (SELECT * FROM dadata_address({}))
SELECT ret_flg, street_code, ret_addr_house, ret_addr_block, ret_addr_flat FROM dd
join shp.dl_streets ds ON ds.search_string = dd.ret_addr_street 
AND ds.city_id IN (SELECT dp.city_id FROM shp.dl_places dp WHERE dp.search_string = dd.ret_addr_city)
"""
curs.execute(addr_sql.format(args.code))
(ret_flag, ret_addr_kladr_street, ret_addr_house, ret_addr_block, ret_addr_flat) = curs.fetchone()

if ret_flag:
    sql_ent = """
        with ent as (SELECT "Предприятия".opf as opf, trim(replace("Предприятие", "Предприятия".opf, '')) as ent_name,
        "ИНН" as inn FROM "Предприятия" WHERE "Код"={})
        select ol.uid, ent.ent_name, ent.inn from ent
        join shp.dl_opf_list ol on ent.opf = ol.opf_name 
        and country_id = (select c.country_id from shp.dl_countries c where c.country_name = 'Россия');
        """.format(args.code)
    curs.execute(sql_ent)
    (opf, name, inn) = curs.fetchone()

    dl = DellinAPI(ark_appkey, user, pw)
    logging.info("logged in sess_id={0}".format(dl.sessionID))

    logging.info('dl.dl_book_counteragents_update(opf={}, name={}, inn={}, kladr_street={}, house={}, building={}, structure={}, flat={});' \
            .format(opf, name, inn, ret_addr_kladr_street, ret_addr_house, ret_addr_block, None, ret_addr_flat))
    res = dl.dl_book_counteragents_update(opf, name, inn,
            street_kladr=ret_addr_kladr_street, 
            house = ret_addr_house, 
            building = ret_addr_block, 
            structure=None,
            flat = ret_addr_flat)
    logging.info('dl_book_counteragents_update res={}'.format(res))
else:
    logging.error('dadata_address returns False')

dl.dl_logout()
