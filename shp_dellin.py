#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base class for api.dellin.ru
"""
import logging
import json
import re

import requests


class DellinAPI(object):
    """
    Base class for api.dellin.ru
    """
    host = "https://api.dellin.ru"
    url_login = '%s/v1/customers/login.json' % host
    url_sfrequest = '%s/v1/customers/sfrequest.json' % host
    url_tracker = '%s/v1/public/tracker.json' % host
    url_tracker_adv = '%s/v1/public/tracker_advanced.json' % host
    url_calculator = '%s/v1/public/calculator.json' % host
    url_logout = '%s/v1/customers/logout.json' % host
    url_orders = '%s/v2/customers/orders.json' % host
    # справочник контрагентов
    url_book_counteragents = '%s/v1/customers/book/counteragents.json' % host
    # наши фирмы, подключённые к ЛК
    url_counteragents = '%s/v1/customers/counteragents.json' % host
    # список адресов контрагента
    url_addresses = '%s/v1/customers/book/addresses.json' % host
    url_dir_countries = '%s/v1/public/countries.json' % host
    url_dir_opf_list = '%s/v1/public/opf_list.json' % host
    url_dir_places = '%s/v1/public/places.json' % host
    url_dir_streets = '%s/v1/public/streets.json' % host
    # Получение списка контактных лиц и телефонов
    url_book_address = '%s/v1/customers/book/address.json' % host
    url_book_counteragents_update = '%s/v1/customers/book/counteragents/update.json' % host
    # добавить или обновить телефон по адресу
    url_phones_update = '%s/v1/customers/book/phones/update.json' % host
    # добавить или обновить контакт по адресу
    url_contacts_update = '%s/v1/customers/book/contacts/update.json' % host
    # добавить или обновить адрес контрагента
    url_addresses_update = '%s/v1/customers/book/addresses/update.json' % host
    url_request = '%s/v1/customers/request.json' % host
    url_request_v2 = '%s/v2/request.json' % host
    # headers = {'Content-type': 'application/javascript'}
    headers = {'Content-type': 'application/json'}

    def __init__(self, app_key, login=None, password=None):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.app_key = app_key
        self.session_id = None
        self.payload = {}
        self.text = ''
        self.status_code = 200
        self.err_msg = None

        if login and password:
            assert isinstance(login, str)
            assert isinstance(password, str)
            self.auth(login, password)

    def auth(self, login, password):
        self.payload = {'login': login,
                        'password': password}
        self.payload.update(self.public_auth())
        resp = self.dl_post(self.url_login)
        if resp is not None:
            self.session_id = resp['sessionID']

    def public_auth(self):
        return {
            'appKey': self.app_key,
        }

    def customers_auth(self):
        return {
            'appKey': self.app_key,
            'sessionID': self.session_id,
        }

    @staticmethod
    def __exception_fmt__(tag, exception):
        return '{0} msg={1}'.format(tag, str(exception).encode('utf-8'))

    def dl_post(self, post_url):
        """ POST an request to api.dellin.ru
            Args:
                post_url - URL on api.dellin.ru
        """
        self.payload['appKey'] = self.app_key
        ret = None
        resp = None
        loc_data = json.dumps(self.payload, ensure_ascii=False)
        logging.debug("url=%s, data=%s", post_url, re.sub(
            r"(.password.\s*:\s*)([\'\"].*?[\'\"])(.*?$)", r"\1 ***** \3"
            , loc_data))
        try:
            resp = requests.post(post_url,
                                 json=self.payload,
                                 headers=self.headers)
            self.status_code = resp.status_code
            self.err_msg = None
            logging.debug("status_code=%s", resp.status_code)
            resp.raise_for_status()
        except requests.exceptions.Timeout as exc:
            # Maybe set up for a retry, or continue in a retry loop
            self.err_msg = self.__exception_fmt__('Timeout', exc)
        except requests.exceptions.TooManyRedirects as exc:
            # Tell the user their URL was bad and try a different one
            self.err_msg = self.__exception_fmt__('TooManyRedirects', exc)
        except requests.exceptions.HTTPError as exc:
            self.err_msg = self.__exception_fmt__('HTTPError', exc)
        except requests.exceptions.RequestException as exc:
            # catastrophic error. bail.
            self.err_msg = self.__exception_fmt__('RequestException', exc)
        else:
            ret = resp.json()
            # logging.debug("r.text=%s", r.text)
        finally:
            if self.err_msg:
                logging.error(self.err_msg)
            if self.status_code != 200:
                logging.error("dl_post failed, status_code=%s", self.status_code)

            if resp is not None:
                self.text = resp.text
                # ??? ONLY for req_v2 ret = resp.json()
                # python2 self.text = resp.text.encode('utf-8')

        return ret

    def dl_tracker_adv(self, sender, receiver, date_start, date_end):
        self.payload = self.customers_auth()
        self.payload["sender"] = {"inn": sender}
        self.payload["receiver"] = {"inn": receiver}
        self.payload["date_start"] = date_start  # "2017-10-19"
        self.payload["date_end"] = date_end  # "2017-10-19"
        return self.dl_post(self.url_tracker_adv)

    def dl_orders(self, docid):
        self.payload = self.customers_auth()
        self.payload["docid"] = docid
        return self.dl_post(self.url_orders)

    def dl_book_counteragents(self):
        self.payload = self.customers_auth()
        return self.dl_post(self.url_book_counteragents)

    def dl_counteragents(self, full_info=False):
        self.payload = self.customers_auth()
        if full_info:
            self.payload["full_info"] = str(full_info)
        return self.dl_post(self.url_counteragents)

    def dl_book_address(self, addr_id):
        """
        Получение списка контактных лиц и телефонов
        """
        self.payload = self.customers_auth()
        self.payload["addressID"] = addr_id
        return self.dl_post(self.url_book_address)

    def dl_addresses(self, ca_id):
        """
        список адресов контрагента
        """
        self.payload = self.customers_auth()
        self.payload["counteragentID"] = ca_id
        return self.dl_post(self.url_addresses)

    def dl_any(self, url):
        self.payload = self.public_auth()
        return self.dl_post(url)

    def dl_request_v1(self, params):
        self.payload = params.copy()
        self.payload.update(self.customers_auth())
        #data = params.copy()
        #data.update(self.customers_auth())
        #logging.info('data=%s'.format(data))

    def dl_request_v2(self, params):
        self.payload = params.copy()
        self.payload.update(self.customers_auth())
        #data = params.copy()
        #data.update(self.customers_auth())
        #logging.info('data=%s'.format(data))

        if self.session_id:
            return self.dl_post(self.url_request_v2)
        else:
            return self.payload

    def dl_test_request(self, params):
        #for k,v in params.items():
        #    logging.info('k=%s, v=%s, dict=%s', k, v, isinstance(v, dict))

        #self.payload = params.copy()
        #self.payload.update(self.customers_auth())
        data = params.copy()
        data.update(self.customers_auth())
        logging.info('data=%s', data)

        if self.session_id:
            # return self.dl_post(self.url_request_v2)
            return requests.post(self.url_request_v2,
                                 data=json.dumps(data), headers=self.headers).json()
        else:
            return self.payload

    def dl_request(self, arc_shipment_id):
        self.payload = self.customers_auth()
        """
        SELECT payload's params from PG by arc_shipment_id

        sender_id, receiver_id, proc_date, totalWeight, totalVolume, quantity, maxLength, maxHeight, maxWidth, maxWeight):
        """
        return self.dl_post(self.url_request)

    def dl_countries(self):
        self.payload = self.public_auth()
        return self.dl_post(self.url_dir_countries)

    def dl_opf_list(self):
        self.payload = self.public_auth()
        return self.dl_post(self.url_dir_opf_list)

    def dl_places(self):
        self.payload = self.public_auth()
        return self.dl_post(self.url_dir_places)

    def dl_streets(self):
        self.payload = self.public_auth()
        return self.dl_post(self.url_dir_streets)

    def dl_book_counteragents_update(self, opf_uid, name, inn, street_kladr, house, building=None, structure=None, flat=None):
        self.payload = self.customers_auth()
        self.payload.update({"form": opf_uid})
        self.payload.update({"name": name})
        self.payload.update({"inn": inn})
        loc_addr = '"street": "{}", "house": "{}"'.format(street_kladr, house)
        if building:
            loc_addr = '{}, "building": "{}"'.format(loc_addr, building)
        if structure:
            loc_addr = '{}, "structure": "{}"'.format(loc_addr, structure)
        if flat:
            loc_addr = '{}, "flat": "{}"'.format(loc_addr, flat)

        loc_addr = '{{{0}}}'.format(loc_addr)
        self.payload.update({"juridicalAddress": json.loads(loc_addr)})
        # DEBUG return json.dumps(self.payload)
        return self.dl_post(self.url_book_counteragents_update)

    def dl_contact_add(self, addr_id, contact_name):
        self.payload = self.customers_auth()
        self.payload.update({"addressID": addr_id})
        self.payload.update({"contact": contact_name})
        return self.dl_post(self.url_contacts_update)

    def dl_contact_update(self, person_id, contact_name):
        self.payload = self.customers_auth()
        self.payload.update({"personID": person_id})
        self.payload.update({"contact": contact_name})
        return self.dl_post(self.url_contacts_update)

    def dl_phone_add(self, addr_id, phone, add_num=None):
        self.payload = self.customers_auth()
        self.payload.update({"addressID": addr_id})
        self.payload.update({"phoneNumber": phone})
        self.payload.update({"addNumber": add_num})
        return self.dl_post(self.url_phones_update)

    def dl_phone_update(self, phone_id, phone, add_num=None):
        self.payload = self.customers_auth()
        self.payload.update({"phoneID": phone_id})
        self.payload.update({"phoneNumber": phone})
        self.payload.update({"addNumber": add_num})
        return self.dl_post(self.url_phones_update)

    def dl_address_add(self, ca_id, street_kladr, house, building=None, structure=None, flat=None):
        self.payload = self.customers_auth()
        self.payload.update({"counteragentID": ca_id})
        self.payload.update({"street": street_kladr})
        self.payload.update({"house": house})
        if building:
            self.payload.update({"building": building})
        if structure:
            self.payload.update({"structure": structure})
        if flat:
            self.payload.update({"flat": flat})
        return self.dl_post(self.url_addresses_update)

    def dl_address_update(self, addr_id, street_kladr=None, house=None, building=None, structure=None, flat=None):
        if street_kladr is None and \
               house is None and \
               building is None and \
               structure is None and \
               flat is None:
            logging.warning('Nothing to update, all arguments are None')
            return None

        self.payload = self.customers_auth()
        self.payload.update({"addressID": addr_id})
        if street_kladr:
            self.payload.update({"street": street_kladr})
        if house:
            self.payload.update({"house": house})
        if building:
            self.payload.update({"building": building})
        if structure:
            self.payload.update({"structure": structure})
        if flat:
            self.payload.update({"flat": flat})

        return self.dl_post(self.url_addresses_update)

    def dl_address_term_add(self, ca_id, term_id):
        self.payload = self.customers_auth()
        self.payload.update({"counteragentID": ca_id})
        self.payload.update({"terminal_id": term_id})
        return self.dl_post(self.url_addresses_update)

    def dl_address_term_update(self, addr_id, term_id):

        self.payload = self.customers_auth()
        self.payload.update({"addressID": addr_id})
        self.payload.update({"terminal_id": term_id})
        return self.dl_post(self.url_addresses_update)

    def dl_logout(self):
        self.payload = self.customers_auth()
        return self.dl_post(self.url_logout)


"""
        def d2j(d):
            loc_str = ''
            loc_list = []
            for k,v in d.items():
                if isinstance(v, dict):
                    loc_str = '"{}": "{}"'.format(k, d2j(v))
                else:
                    loc_str = '"{}": "{}"'.format(k, v)
                loc_list.append(loc_str)    
            loc_str = ','.join(loc_list)
            return '{{{}}}'.format(loc_str)
"""
