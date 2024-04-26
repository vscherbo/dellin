#!/usr/bin/env python
""" DL labels
"""
import base64
import logging
# import argparse
# import configparser
#from dl_app import DL_app
import sys

import dl_app


class DlLabel(dl_app.DL_app):
    """ Class for asking and getting DL labels """
    def __init__(self, args, description='DL labels: asking and getting'):
        super().__init__(args, description)
        #if not self.login():
        #    logging.error('DL login failed')

    def ask(self, arg_req_id, arg_shp_id, arg_boxes):
        """ Ask DL to generate label(-s) """
        ret_str = None
        dl_res = self.dl.dl_labels(arg_req_id, arg_shp_id, arg_boxes)
        logging.info('dl_labels: dl_res=%s', dl_res)
        if dl_res['metadata']['status'] == 200 and dl_res['data']['state'] == 'enqueued':
            logging.info('%s', dl_res['data'])
        elif "errors" in dl_res.keys():
            logging.error("dl_labels errors=%s", dl_res["errors"])
            err_list = []
            for err in dl_res["errors"]:
                err_list.append(f'{err["detail"]}: {err["fields"]}')

            err_str = ' ,'.join(err_list)
            #print(err_str, file=sys.stderr, end='', flush=True)
            ret_str = err_str
        return ret_str

    def get(self, arg_req_id, arg_out_dir='.', arg_type='pdf', arg_format='80x50'):
        """ Get label(-s) from DL """
        ret_str = None
        dl_res = self.dl.dl_get_labels(arg_req_id, arg_format=arg_format, arg_type=arg_type)
        if dl_res is None:
            ret_str = "dl_get_labels res is None"
            logging.error(ret_str)
        elif "errors" in dl_res.keys():
            logging.error("dl_get_labels errors=%s", dl_res["errors"])
            err_list = []
            for err in dl_res["errors"]:
                err_list.append(f'{err["detail"]}: {err["fields"]}')

            err_str = ' ,'.join(err_list)
            #print(err_str, file=sys.stderr, end='', flush=True)
            ret_str = err_str
        elif self.dl.status_code == 200 and dl_res['metadata']['totalPages'] > 0:
            filename = f'{arg_out_dir}/{arg_req_id}.{arg_type}'
            with open(filename, "wb") as barcode_output:
                try:
                    # TODO downloaded multiple labels
                    content = base64.b64decode(dl_res["data"][0]["base64"])
                    barcode_output.write(content)
                except (IndexError, AttributeError):
                    logging.error('dl_res=%s', dl_res)
                    ret_str = 'write label to file failed'
                    logging.exception(ret_str)
        else:
            ret_str = 'a label is not ready yet'
            logging.warning('UNEXPECTED dl_res=%s', dl_res)
        return ret_str

def main():
    """ Just main """

    dl_app.parser.add_argument('--req_id', type=int, required=True, help='DL tracking number')
    dl_app.parser.add_argument('--mode', type=str, required=True, choices=['ask', 'get'],
            help='provide request number or get labels')
    # mode 'ask'
    dl_app.parser.add_argument('--shp_id', type=int, help='shp_id')
    dl_app.parser.add_argument('--boxes', type=int, help='number of boxes for req_id')
    # mode 'get'
    dl_app.parser.add_argument('--out_dir', type=str, default='.', help='output directory')
    dl_app.parser.add_argument('--type', type=str, help='DL-label type: pdf(default), jpg, png')
    dl_app.parser.add_argument('--format', type=str, help='DL-label format: 80x50(default), a4')
    args = dl_app.parser.parse_args()


    dl_labels = DlLabel(args=args, description='DL labels')
    logging.info("args=%s", args)
    dl_labels.login(auth=True)

    if args.mode == 'ask':
        ret_str = dl_labels.ask(args.req_id, args.shp_id, args.boxes)
    elif args.mode == 'get':
        ret_str = dl_labels.get(args.req_id)

    if ret_str is not None and ret_str != '':
        print(ret_str, file=sys.stderr, end='', flush=True)

    dl_labels.logout()


def main1():
    """ Just main """

    dl_app.parser.add_argument('--req_id', type=int, required=True, help='DL tracking number')
    dl_app.parser.add_argument('--mode', type=str, required=True, choices=['ask', 'get'],
            help='provide request number or get labels')
    # mode 'ask'
    dl_app.parser.add_argument('--shp_id', type=int, help='shp_id')
    dl_app.parser.add_argument('--boxes', type=int, help='number of boxes for req_id')
    # mode 'get'
    dl_app.parser.add_argument('--out_dir', type=str, default='.', help='output directory')
    dl_app.parser.add_argument('--type', type=str, help='DL-label type: pdf(default), jpg, png')
    dl_app.parser.add_argument('--format', type=str, help='DL-label format: 80x50(default), a4')
    args = dl_app.parser.parse_args()


    dl_labels = dl_app.DL_app(args=args, description='DL labels')
    logging.info("args=%s", args)
    dl_labels.login(auth=True)

    if args.mode == 'ask':
        dl_res = dl_labels.dl.dl_labels(args.req_id, args.shp_id, args.boxes)
        logging.info('dl_labels: dl_res=%s', dl_res)
        if dl_res['metadata']['status'] == 200 and dl_res['data']['state'] == 'enqueued':
            logging.info('%s', dl_res['data'])
        elif "errors" in dl_res.keys():
            logging.error("dl_labels errors=%s", dl_res["errors"])
            err_str = ' ,'.join([dl_res["errors"][0]["title"]] + dl_res["errors"][0]["fields"])
            print(err_str, file=sys.stderr, end='', flush=True)
    else:  # 'get'
        if args.type is None:
            ext = 'pdf'
        else:
            ext = args.type

        if args.format is None:
            out_format = '80x50'
        else:
            out_format = args.type


        dl_res = dl_labels.dl.dl_get_labels(args.req_id, arg_format=out_format, arg_type=ext)
        if dl_res is None:
            logging.error("dl_get_labels res is None")
        elif "errors" in dl_res.keys():
            logging.error("dl_get_labels errors=%s", dl_res["errors"])
            err_str = ' ,'.join([dl_res["errors"][0]["title"]] + dl_res["errors"][0]["fields"])
            print(err_str, file=sys.stderr, end='', flush=True)
        elif dl_labels.dl.status_code == 200:


            filename = f'{args.out_dir}/{args.req_id}.{ext}'
            with open(filename, "wb") as barcode_output:
                try:
                    content = base64.b64decode(dl_res["data"][0]["base64"])
                    barcode_output.write(content)
                except (IndexError, AttributeError):
                    logging.error('dl_res=%s', dl_res)
                    logging.error('err=%s', dl_labels.dl.err_msg)


            logging.info('dl_res=%s', dl_res)

    dl_labels.dl.dl_logout()


if __name__ == '__main__':
    main()
