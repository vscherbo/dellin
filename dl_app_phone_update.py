#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
import sys
import dl_app

dl_app.parser.add_argument('--phone_id', type=int, required=True, help='phone_id') 
dl_app.parser.add_argument('--phone', type=str, required=True, help='phone number') 
dl_app.parser.add_argument('--add_num', type=str, required=False, help='extention number') 
args = dl_app.parser.parse_args()

app = dl_app.DL_app(args=args, description='DL phone update')
logging.info("args={}".format(args))

if app.login(auth=True):
    dl_res = app.dl.dl_phone_update(args.phone_id, args.phone, args.add_num)

    logging.info('dl_res={}'.format(dl_res))
    # OUTPUT: dl_res={'success': ....
    if 200 == app.dl.status_code:
        if 'success' in dl_res:
            ret_phone_id = dl_res['success']['phoneID']
            logging.info('state={}, phoneID={}'.format(
                dl_res['success']['state'],
                ret_phone_id))
            print(ret_phone_id, end='', flush=True)
            app.db_login()
            curs = app.conn.cursor()
            if args.phone and args.add_num:
                loc_sql = curs.mogrify('UPDATE ext.dl_addr_phone set phone=%s, "addNumber"=%s, status=%s WHERE id=%s;',
                            (args.phone, args.add_num, 1, args.phone_id ))
            else:
                loc_sql = curs.mogrify('UPDATE ext.dl_addr_phone set phone=%s, status=%s WHERE id=%s;',
                            (args.phone, 1, args.phone_id ))
            logging.info("loc_sql={}".format(loc_sql))
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
