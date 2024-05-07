#!/usr/bin/env python
""" A listener for Dellin notifications
"""

#import argparse
import logging
import os
import select
import signal
from os.path import expanduser
#from sys import exc_info  # , exit
from time import sleep

import log_app
import paramiko
#import psycopg2
import psycopg2.extensions
from pg_app import PGapp
from scp import SCPClient
from sig_app import Application

import dl_labels

# pg_channels = ('do_export', 'do_compute_single', 'do_expected')
pg_channels = ('get_dl_label', )
PG_TIMEOUT = 5
# PROD:
MARK_DISPLAY = 3600

SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n) for n in dir(signal)
                             if n.startswith('SIG') and '_' not in n)

UPD_LBL = \
"UPDATE shp.dl_labels_q SET status = %s, err_msg = %s, last_dt = now() WHERE prereq_id = %s;"

#class KeepalivesFilter (object):
#    def filter(self, record):
#        return record.msg.find('keepalive@openssh.com') < 0


class PgListener(Application, PGapp, log_app.LogApp):
    """ PG "notify" signal handler """
    def __init__(self, args):
        log_app.LogApp.__init__(self, args=args)
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        self.get_config(f'{script_name}.conf')
        super().__init__()
        PGapp.__init__(self, self.config['PG']['pg_host'], self.config['PG']['pg_user'])
        self.pg_channels = args.pg_channels
        self.do_while = False
        self.dl_labels = dl_labels.DlLabel(args=args, description='DL labels')
        self.dl_labels.login(auth=True)

    def _signal_handler(self):
        """ A signals handler """
        logging.info('PgListener signal_handler')
        self.do_while = False
        super()._signal_handler()

    def close(self):
        """ finalize """
        self.pg_close()

    def _main(self):
        """ Just main """
        logging.info("Started")
        if self.pg_connect():
            self.set_session(autocommit=True)
            self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            logging.info('PG connected')
        #sel_res = ([], [], [])
        for pg_channel in self.pg_channels:
            try:
                #self.curs.execute(f"LISTEN {pg_channel};")
                self.do_query(f"LISTEN {pg_channel};", reconnect=True)
                logging.debug('...listening %s', pg_channel)
            except psycopg2.Error as exc:  # TODO handle real exceptions
                logging.warning(" Exception on LISTEN(%s)=%s. Sleep for %s", pg_channel,
                        str(exc), str(PG_TIMEOUT))
                sleep(PG_TIMEOUT)
            else:
                logging.info("Waiting for notifications on channel %s", pg_channel)
        mark_counter = 0
        self.do_while = True

        # main loop
        while self.do_while:
            self.do_listen()
            mark_counter += PG_TIMEOUT
            if mark_counter >= MARK_DISPLAY:
                mark_counter=0
                logging.info("Heartbeat mark")

    def do_listen(self):
        """ Do listen"""
        sel_res = select.select([self.conn], [], [], PG_TIMEOUT)
        if sel_res == ([], [], []):
            pass  # logging.debug('listen timeout')
        else:
            self.conn.poll()
            while self.conn.notifies:
                notify = self.conn.notifies.pop(0)
                logging.info("=========================================")
                logging.info("Got NOTIFY: %s %s %s", notify.pid, notify.channel, notify.payload)
                if 'ask_dl_label' == notify.channel:
                    self.ask_label(notify)
                elif 'get_dl_label' == notify.channel:
                    sleep(1)  # to finish making label
                    self.get_label(notify)
                else:
                    logging.info("unexpected notify.channel=%s", notify.channel)
                self.conn.commit()


    def ask_label(self, notify):
        """ Call DL API method to make labels """
        logging.debug("     Inside ask_label")
        (req_id, shp_id, boxes) = notify.payload.split()
        #(req_id, shp_id, boxes, first_bill) = notify.payload.split()
        logging.debug("notify.payload: req_id=%s, shp_id=%s, boxes=%s",
                req_id, shp_id, boxes)
        ret_str = self.dl_labels.ask(req_id, shp_id, boxes)
        try:
            loc_status = 'enqueued'
            if ret_str is not None \
               and 'Запрос на передачу грузомест по заказу уже выполняется' not in ret_str:
                loc_status = 'enqueue-err'

            upd_cmd = self.curs.mogrify(UPD_LBL, (loc_status, ret_str, req_id))
            logging.info("upd_cmd=%s", upd_cmd)
            self.curs.execute(upd_cmd)
        except psycopg2.Error as exc:
            logging.error("_exception_UPDATE dl_labels_q=%s", str(exc))
        else:
            logging.info("TRY-ELSE: upd Ok")
            self.conn.commit()

    def get_label(self, notify):
        """ Call DL API method to download labels """
        logging.debug("     Inside get_label")
        (req_id, label_type, label_format) = notify.payload.split()
        logging.debug("notify.payload: req_id=%s, label_type=%s, label_format=%s",
                req_id, label_type, label_format)
        (ret_str, filename) = self.dl_labels.get(req_id, './jpg', arg_type=label_type,
                arg_format=label_format)
        loc_status = 'got'
        if ret_str is not None:
            if 'not ready' in ret_str:
                loc_status = 'not-ready'
            else:
                loc_status = 'get-err'
        else:
            # copy to FNAS
            logging.info('try to scp %s', filename)
            try:
                self._scp(filename)
            except Exception as err:
                logging.exception(f"Unexpected err={err}, type={type(err)}")
            else:
               loc_status = 'published'

        try:
            upd_cmd = self.curs.mogrify(UPD_LBL, (loc_status, ret_str, req_id))
            logging.info("upd_cmd=%s", upd_cmd)
            self.curs.execute(upd_cmd)
        except psycopg2.Error as exc:
            logging.error("_exception_UPDATE dl_labels_q=%s", str(exc))
        else:
            logging.info("TRY-ELSE: upd Ok")
            self.conn.commit()

    def _scp(self, arg_file):
        """ Doing scp """
        #paramiko.util.get_logger('paramiko.transport').addFilter(KeepalivesFilter())
        home_dir = expanduser("~")
        logging.info("home_dir=%s", home_dir)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        #loc_key = paramiko.RSAKey.from_private_key_file(home_dir + "/.ssh/id_rsa")
        try:
            #ssh.connect('cifs-public.arc.world', username='uploader', pkey=loc_key)
            ssh.connect('cifs-public.arc.world', username='uploader')
        except paramiko.ssh_exception.AuthenticationException:
            logging.error('Authentication failed')
        except Exception as err:
            logging.exception(f"Unexpected err={err}, type={type(err)}")
            raise
        else:
            # SCPCLient takes a paramiko transport as an argument
            scp = SCPClient(ssh.get_transport())

            scp.put(arg_file, '/mnt/r10/ds_cifs/public/от ИТ/для Упаковки/ДЛ/labels/')

            scp.close()



if __name__ == '__main__':
    log_app.PARSER.add_argument('--pg_channels', nargs='+', required=True,
            help='PG channels to listen')

    ARGS = log_app.PARSER.parse_args()
    APP = PgListener(args=ARGS)
    paramiko.util.get_logger('paramiko.transport').setLevel(logging.INFO)
    #.addFilter(KeepalivesFilter())
    APP.main_loop()
    APP.close()
    logging.info("Exiting")
