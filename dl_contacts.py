#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
# import argparse
# import configparser
from dl_app import DL_app


dl_contacts = DL_app('DL contact add')
dl_contacts.login(auth=True)

# dl_res = dl_contacts.dl.dl_contact_add(20463457, 'Щербо Владимир')
# return personID 83863756

dl_res = dl_contacts.dl.dl_contact_update(83863756, 'Щербо В.А.')

logging.info('dl_res={}'.format(dl_res))

dl_contacts.dl.dl_logout()
