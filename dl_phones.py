#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
# import argparse
# import configparser
from dl_app import DL_app


dl_phones = DL_app('DL phone add')
dl_phones.login(auth=True)

# BAD formats
# dl_res = dl_phones.dl.dl_phone_add(18871664, '1234567890 0987654321')
# dl_res = dl_phones.dl.dl_phone_add(18871664, '12345')
# dl_res = dl_phones.dl.dl_phone_add(18871664, '12345789')
# dl_res = dl_phones.dl.dl_phone_add(18871664, '+8(921)-917-65 97; 123')


# dl_res = dl_phones.dl.dl_phone_add(18871664, '1234567890')  # good
# dl_res = dl_phones.dl.dl_phone_add(18871664, '+7(921)-917-65 97')  # good
# dl_res = dl_phones.dl.dl_phone_add(18871664, '+8(921)-917-65 97')  # good
dl_res = dl_phones.dl.dl_phone_add(18871664, '+8(921)-917-65 97 123')

logging.info('dl_res={}'.format(dl_res))

dl_phones.dl.dl_logout()
