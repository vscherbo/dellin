#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
import json
import re


class DellinAPI:
    host = "https://api.dellin.ru"
    url_login = '{}/v1/customers/login.json'.format(host)
    url_sfrequest = '{}/v1/customers/sfrequest.json'.format(host)
    url_tracker = '{}/v1/public/tracker.json'.format(host)
    url_tracker_adv = '{}/v1/public/tracker_advanced.json'.format(host)
    url_calculator = '{}/v1/public/calculator.json'.format(host)
    url_logout = '{}/v1/customers/logout.json'.format(host)
    url_orders = '{}/v2/customers/orders.json'.format(host)
    url_book_counteragents = '{}/v1/customers/book/counteragents.json'.format(host)  # справочник контрагентов
    url_counteragents = '{}/v1/customers/counteragents.json'.format(host)  # наши фирмы, подключённые к ЛК
    url_addresses = '{}/v1/customers/book/addresses.json'.format(host)  # список адресов контрагента
    url_dir_countries = '{}/v1/public/countries.json'.format(host)
    url_dir_opf_list = '{}/v1/public/opf_list.json'.format(host)
    url_dir_places = '{}/v1/public/places.json'.format(host)
    url_dir_streets = '{}/v1/public/streets.json'.format(host)
    url_book_address = '{}/v1/customers/book/address.json'.format(host)  # Получение списка контактных лиц и телефонов
    url_book_counteragents_update = '{}/v1/customers/book/counteragents/update.json'.format(host)
    url_phones_update = '{}/v1/customers/book/phones/update.json'.format(host)  # добавить или обновить телефон по адресу
    url_contacts_update = '{}/v1/customers/book/contacts/update.json'.format(host)  # добавить или обновить контакт по адресу
    url_addresses_update = '{}/v1/customers/book/addresses/update.json'.format(host)  # добавить или обновить адрес контрагента
    url_request = '{}/v1/customers/request.json'.format(host)
    # headers = {'Content-type': 'application/javascript'}
    headers = {'Content-type': 'application/json'}

    def __init__(self, app_key, login=None, password=None):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.app_key = app_key
        self.sessionID = None
        self.payload = {}
        self.text = ''
        self.status_code = 0

        if login and password:
            assert isinstance(login, str)
            assert isinstance(password, str)
            self.auth(login, password)

    def auth(self, login, password):
        self.payload = {'login': login,
                        'password': password}
        self.payload.update(self.public_auth())
        r = self.dl_post(self.url_login)
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

    def dl_post(self, post_url):
        self.payload['appKey'] = self.app_key
        ret = None
        r = None
        try:
            loc_data = json.dumps(self.payload)
            logging.debug("url={0}, data={1}".format(post_url, re.sub(r'"password": (.*)}', "'*****'",loc_data)))
            r = requests.post(post_url, json=self.payload, headers=self.headers)
            self.status_code = r.status_code
            logging.debug("status_code={}".format(r.status_code))
            # logging.debug("r.headers={}".format(r.headers))
            # logging.debug("r.url={}".format(r.url))
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
            # logging.debug("r.text={}".format(r.text))
        finally:
            if r is not None:
                self.text = r.text
                # P2 self.text = r.text.encode('utf-8')

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

    def dl_counteragents(self, full_info = False):
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

    def dl_request(self, arc_shipment_id):
        self.payload = self.customers_auth()
        """
        SELECT payload's params from PG by arc_shipment_id
        sender_id, receiver_id, proc_date, totalWeight, totalVolume, quantity, maxLength, maxHeight, maxWidth, maxWeight):
        """
        self.payload.update({"form": opf_uid})
        self.payload.update({"name": name})
        if building:
            loc_addr = '{}, "building": "{}"'.format(loc_addr, building)
        if structure:
            loc_addr = '{}, "structure": "{}"'.format(loc_addr, structure)
        if flat:
            loc_addr = '{}, "flat": "{}"'.format(loc_addr, flat)

        loc_addr = '{{{0}}}'.format(loc_addr)
        self.payload.update({"sender": json.loads(loc_addr)})

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
        # self.payload["juridicalAddress"] = """{{"street": "{}", "house": "{}", "building": "{}", "structure": "{}", "flat": "{}"}}""".format(\
        #        street_kladr, house, building, structure, flat)
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
        if street_kladr is None and house is None and building is None and structure is None and flat is None:
            logging.warning('Nothing to update, all arguments are None')
            return json(None)

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
