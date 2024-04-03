#!/usr/bin/env python3

import argparse
import configparser
import logging
import sys

import psycopg2

from shp_dellin import DellinAPI


class DL_app(object):
    log_format = '[%(filename)-21s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'
    conf_file_name = "dl.conf"

    def __init__(self, args, description='Dellin application'):
        self.args = args
        self.dl = None
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        numeric_level = getattr(logging, self.args.log_level, None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % numeric_level)

        if 'stdout' == self.args.log_file:
            logging.basicConfig(stream=sys.stdout, format=self.log_format, level=numeric_level)
        else:
            logging.basicConfig(filename=self.args.log_file, format=self.log_format, level=numeric_level)

        config = configparser.ConfigParser(allow_no_value=True)
        config.read(self.args.conf)
        self.API_KEY = config['dadata_login']['API_KEY']

        self.ark_appkey = config['dl_login']['ark_appkey']
        self.user = config['dl_login']['user']
        self.pw = config['dl_login']['pw']
        self.conn = None


    def login(self, auth=False):
        if auth:
            self.dl = DellinAPI(self.ark_appkey, self.user, self.pw)
        else:
            self.dl = DellinAPI(self.ark_appkey)
        loc_return = (200 == self.dl.status_code)
        if loc_return:
            logging.info("logged in sess_id=%s", self.dl.session_id)
        else:
            logging.error("loggin error. status_code=%d, err_msg=%s", self.dl.status_code, self.dl.err_msg)
        return loc_return


    def db_login(self):
        logging.debug('args=%s', self.args)
        if self.args.pg_srv is not None:
            self.conn = psycopg2.connect("host='" + self.args.pg_srv + "' dbname='arc_energo' user='arc_energo'")  # password='XXXX' - .pgpass

    def logout(self):
        self.dl.dl_logout()
        if self.conn and not self.conn.closed:
            self.conn.commit()
            self.conn.close()

conf_file_name = "dl.conf"
parser = argparse.ArgumentParser()
parser.add_argument('--conf', type=str, default=conf_file_name, help='conf file')
parser.add_argument('--pg_srv', type=str, default='localhost', help='PG hostname')
parser.add_argument('--log_file', type=str, default='stdout', help='log destination')
parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
