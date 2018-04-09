# -*- coding: utf-8 -*-

import logging
import types
import requests


class DellinAPI:
    host = "https://api.dellin.ru"
    url_login = '{}/v1/customers/login.json'.format(host)
    url_sfrequest = '{}/v1/customers/sfrequest.json'.format(host)
    url_tracker = '{}/v1/public/tracker.json'.format(host)
    url_tracker_adv = '{}/v1/public/tracker_advanced.json'.format(host)
    url_calculator = '{}/v1/public/calculator.json'.format(host)
    url_logout = '{}/v1/customers/logout.json'.format(host)
    url_orders = '{}/v2/customers/orders.json'.format(host)
    url_counteragents = '{}/v1/customers/book/counteragents.json'.format(host)
    url_addresses = '{}/v1/customers/book/addresses.json'.format(host)
    headers = {'Content-type': 'application/javascript'}

    def __init__(self, app_key, login=None, password=None):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.app_key = app_key
        self.sessionID = None
        self.payload = {}
        self.text = ''

        if login and password:
            assert isinstance(login, types.StringType)
            assert isinstance(password, types.StringType)
            self.auth(login, password)

    def auth(self, login, password):
        self.payload = {'login': login,
                        'password': password}
        self.payload.update(self.public_auth())
        r = self.dl_get(self.url_login)
        if r is not None:
            self.sessionID = r['sessionID']

    def public_auth(self):
        return {
            'appKey': self.app_key,
        }

    def customers_auth(self):
        return {
            'appKey': self.app_key,
            'sessionID': self.sessionID,
        }

    @staticmethod
    def __exception_fmt__(tag, exception):
        return '{0} msg={1}'.format(tag, str(exception).encode('utf-8'))

    def dl_get(self, get_url):
        self.payload['appKey'] = self.app_key
        ret = None
        r = None
        try:
            logging.debug('{0}/{1}'.format(get_url, self.payload))
            r = requests.post(get_url, json=self.payload)
            logging.debug("status_code={}".format(r.status_code))
            r.raise_for_status()
        except requests.exceptions.Timeout as e:
            # Maybe set up for a retry, or continue in a retry loop
            logging.error(self.__exception_fmt__('Timeout', e))
        except requests.exceptions.TooManyRedirects as e:
            # Tell the user their URL was bad and try a different one
            logging.error(self.__exception_fmt__('TooManyRedirects', e))
        except requests.exceptions.HTTPError as e:
            logging.error(self.__exception_fmt__('HTTPError', e))
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            logging.error(self.__exception_fmt__('RequestException', e))
        else:
            ret = r.json()
        finally:
            if r is not None:
                self.text = r.text.encode('utf-8')

        return ret

    def dl_tracker_adv(self, sender, receiver, date_start, date_end):
        self.payload = self.customers_auth()
        self.payload["sender"] = {"inn": sender}
        self.payload["receiver"] = {"inn": receiver}
        self.payload["date_start"] = date_start  # "2017-10-19"
        self.payload["date_end"] = date_end  # "2017-10-19"
        return self.dl_get(self.url_tracker_adv)

    def dl_orders(self, docid):
        self.payload = self.customers_auth()
        self.payload["docid"] = docid
        return self.dl_get(self.url_orders)

    def dl_counteragents(self):
        self.payload = self.customers_auth()
        return self.dl_get(self.url_counteragents)

    def dl_addresses(self, ca_id):
        self.payload = self.customers_auth()
        self.payload["counteragentID"] = ca_id
        return self.dl_get(self.url_addresses)

    def dl_any(self, url):
        self.payload = self.customers_auth()
        return self.dl_get(url)

    def dl_logout(self):
        self.payload = self.customers_auth()
        return self.dl_get(self.url_logout)
