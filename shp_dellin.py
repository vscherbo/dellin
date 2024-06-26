#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base class for api.dellin.ru
"""
import json
import logging
import re

import requests


class DellinAPI():
    """
    Base class for api.dellin.ru
    """
    host = "https://api.dellin.ru"
    url_login = f"{host}/v1/customers/login.json"
    url_sfrequest = f"{host}/v1/customers/sfrequest.json"
    url_tracker = f"{host}/v2/public/tracker.json"
    url_tracker_adv = f"{host}/v1/public/tracker_advanced.json"
    url_calculator = f"{host}/v1/public/calculator.json"
    url_logout = f"{host}/v1/customers/logout.json"
    url_orders = f"{host}/v2/customers/orders.json"
    url_orders_v3 = f"{host}/v3/orders.json"
    # справочник контрагентов
    url_book_counteragents = f"{host}/v1/customers/book/counteragents.json"
    url_book_counteragents_v2 = f"{host}/v2/book/counteragents.json"
    # наши фирмы, подключённые к ЛК
    url_counteragents = f"{host}/v1/customers/counteragents.json"
    # список адресов контрагента
    url_addresses = f"{host}/v1/customers/book/addresses.json"
    url_dir_countries = f"{host}/v1/public/countries.json"
    url_dir_opf_list = f"{host}/v1/public/opf_list.json"
    url_dir_places = f"{host}/v1/public/places.json"
    url_dir_streets = f"{host}/v1/public/streets.json"
    # Получение списка контактных лиц и телефонов
    url_book_address = f"{host}/v1/customers/book/address.json"
    url_book_counteragents_update = f"{host}/v1/customers/book/counteragents/update.json"
    url_book_counteragents_update_v2 = f"{host}/v2/book/counteragent/update.json"
    # добавить или обновить телефон по адресу
    url_phones_update = f"{host}/v1/customers/book/phones/update.json"
    # добавить или обновить контакт по адресу
    url_contacts_update = f"{host}/v1/customers/book/contacts/update.json"
    # добавить или обновить адрес контрагента
    url_addresses_update = f"{host}/v1/customers/book/addresses/update.json"
    url_addresses_update_v2 = f"{host}/v2/book/address/update.json"
    url_request = f"{host}/v1/customers/request.json"
    url_request_v2 = f"{host}/v2/request.json"
    url_book_delete = f"{host}/v1/customers/book/delete.json"
    url_printable = f"{host}/v1/printable.json"
    url_labels = f"{host}/v2/request/cargo/shipment_labels.json"
    url_get_labels = f"{host}/v2/request/cargo/shipment_labels/get.json"
    url_counteragents_v2 = f"{host}/v2/counteragents.json"
    headers = {'Content-type': 'application/json', 'User-Agent': 'Python'}

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
            self._auth(login, password)

    def _auth(self, login, password):
        """
        Perform authentication.

        Args:
            login (str): The login name.
            password (str): The password.
        """
        self.payload = {'login': login,
                        'password': password}
        self.payload.update(self._public_auth())
        resp = self._dl_post(self.url_login)
        if resp is not None and 'sessionID' in resp.keys():
            self.session_id = resp['sessionID']
        else:
            self.status_code = -1


    def _public_auth(self):
        return {
            'appKey': self.app_key,
        }

    def _customers_auth(self):
        return {
            'appKey': self.app_key,
            'sessionID': self.session_id,
        }

    @staticmethod
    def __exception_fmt__(tag, exception):
        return f'{tag} msg={str(exception).encode("utf-8")}'

    def _dl_post(self, post_url):
        """ POST an request to api.dellin.ru
            Args:
                post_url - URL on api.dellin.ru
        """
        self.payload['appKey'] = self.app_key
        ret = None
        resp = None
        loc_data = json.dumps(self.payload, ensure_ascii=False)
        logging.debug("url=%s, data=%s", post_url, re.sub(
            r"(.password.\s*:\s*)([\'\"].*?[\'\"])(.*?$)", r"\1 ***** \3",
            loc_data))
        try:
            resp = requests.post(post_url,
                                 timeout=30,
                                 json=self.payload,
                                 headers=self.headers)
            self.status_code = resp.status_code
            self.err_msg = None
            logging.debug("status_code=%s", resp.status_code)
            resp.raise_for_status()
        except TypeError as exc:
            self.err_msg = self.__exception_fmt__('TypeError', exc)
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
        except Exception as exc:
            # catastrophic error. bail.
            self.err_msg = self.__exception_fmt__('other Exception', exc)
        else:
            ret = resp.json()
            #logging.debug("resp.text=%s", resp.text)
        finally:
            if self.err_msg:
                logging.error(self.err_msg)
                ret = {}
                if resp is not None:
                    try:
                        ret = resp.json()  # v2 API
                        logging.error(resp.json())
                    #except requests.exceptions.JSONDecodeError:
                    except:
                        logging.error(resp.text)
                        #ret = resp  # ??? .text
                        ret = {}

                ret["answer"] = {'state': 'exception', 'err_msg': self.err_msg}
            elif self.status_code != 200:
                logging.error("_dl_post failed, status_code=%s",
                              self.status_code)

            if resp is not None:
                self.text = resp.text
                # ??? ONLY for req_v2 ret = resp.json()
                # python2 self.text = resp.text.encode('utf-8')

        return ret

    def dl_tracker(self, doc_id):
        """
        Get tracker information for a document.

        Args:
            doc_id (str): The document ID.

        Returns:
            dict: The response JSON.
        """

        self.payload = self._customers_auth()
        self.payload["docid"] = doc_id
        return self._dl_post(self.url_tracker)


    def dl_tracker_adv(self, sender, receiver, date_start, date_end):
        self.payload = self._customers_auth()
        self.payload["sender"] = {"inn": sender}
        self.payload["receiver"] = {"inn": receiver}
        self.payload["date_start"] = date_start  # "2017-10-19"
        self.payload["date_end"] = date_end  # "2017-10-19"
        return self._dl_post(self.url_tracker_adv)

    def dl_orders(self, docid):
        self.payload = self._customers_auth()
        self.payload["docIds"] = docid
        return self._dl_post(self.url_orders)

    def dl_orders_v3(self, docid):
        self.payload = self._customers_auth()
        self.payload["docIds"] = docid
        return self._dl_post(self.url_orders_v3)

    def dl_book_counteragents_v2(self, ca_id):
        self.payload = self._customers_auth()
        self.payload["counteragentIds"] = [ca_id]
        return self._dl_post(self.url_book_counteragents_v2)

    def dl_book_counteragents_list(self, ca_ids):
        self.payload = self._customers_auth()
        self.payload["counteragentIds"] = ca_ids
        return self._dl_post(self.url_book_counteragents_v2)

    def dl_book_counteragents_full(self):
        self.payload = self._customers_auth()
        #self.payload["counteragentIds"] = ca_ids
        return self._dl_post(self.url_book_counteragents_v2)

    def dl_book_counteragents(self):
        self.payload = self._customers_auth()
        return self._dl_post(self.url_book_counteragents)

    def dl_counteragents(self, full_info=False):
        self.payload = self._customers_auth()
        if full_info:
            self.payload["full_info"] = str(full_info)
        return self._dl_post(self.url_counteragents)

    def dl_book_address(self, addr_id):
        """
        Получение списка контактных лиц и телефонов
        """
        self.payload = self._customers_auth()
        self.payload["addressID"] = addr_id
        return self._dl_post(self.url_book_address)

    def dl_addresses(self, ca_id):
        """
        список адресов контрагента
        """
        self.payload = self._customers_auth()
        self.payload["counteragentID"] = ca_id
        return self._dl_post(self.url_addresses)

    def dl_any(self, url):
        self.payload = self._public_auth()
        return self._dl_post(url)

    def dl_request_v1(self, params):
        self.payload = params.copy()
        self.payload.update(self._customers_auth())
        # data = params.copy()
        # data.update(self._customers_auth())
        # logging.info('data=%s'.format(data))
        if self.session_id:
            return self._dl_post(self.url_request)
            # return requests.post(self.url_request, data=json.dumps(data),
            #                      headers=self.headers).json()
        else:
            return self.payload

    def dl_test_request(self, params):
        # for k,v in params.items():
        #    logging.info('k=%s, v=%s, dict=%s', k, v, isinstance(v, dict))

        # self.payload = params.copy()
        # self.payload.update(self._customers_auth())
        data = params.copy()
        data.update(self._customers_auth())
        logging.info('data=%s', data)

        if self.session_id:
            # return self._dl_post(self.url_request_v2)
            return requests.post(self.url_request_v2,
                                 data=json.dumps(data),
                                 headers=self.headers).json()
        else:
            return self.payload

    def dl_request_v2(self, params):
        """ Do request via API v2 """
        self.payload = params.copy()
        self.payload.update(self._customers_auth())
        # data = params.copy()
        # data.update(self._customers_auth())
        # logging.info('data=%s'.format(data))

        if self.session_id:
            res = self._dl_post(self.url_request_v2)
        else:
            res = self.payload
        return res

    def dl_request(self, arc_shipment_id):
        self.payload = self._customers_auth()
        """
        SELECT payload's params from PG by arc_shipment_id

        sender_id, receiver_id, proc_date, totalWeight, totalVolume, quantity,
        maxLength, maxHeight, maxWidth, maxWeight):
        """
        return self._dl_post(self.url_request)

    def dl_countries(self):
        self.payload = self._public_auth()
        return self._dl_post(self.url_dir_countries)

    def dl_opf_list(self):
        self.payload = self._public_auth()
        return self._dl_post(self.url_dir_opf_list)

    def dl_places(self):
        self.payload = self._public_auth()
        return self._dl_post(self.url_dir_places)

    def dl_streets(self):
        self.payload = self._public_auth()
        return self._dl_post(self.url_dir_streets)

    def dl_book_counteragents_update(self, opf_uid, name, inn, street_kladr,
                                     house,
                                     building=None, structure=None, flat=None):
        """ OBSOLETE создание и обновление контрагента-юр.лицо
        """
        self.payload = self._customers_auth()
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
        return self._dl_post(self.url_book_counteragents_update)

    def dl_book_ca_update(self, params):
        """ создание и обновление контрагента
        """
        self.payload = params.copy()
        self.payload.update(self._customers_auth())

        if self.session_id:
            return self._dl_post(self.url_book_counteragents_update)
        else:
            return self.payload

    def dl_book_ca_update_v2(self, params):
        """ создание и обновление контрагента
        """
        self.payload = params.copy()
        self.payload.update(self._customers_auth())

        if self.session_id:
            return self._dl_post(self.url_book_counteragents_update_v2)
        else:
            return self.payload

    def dl_contact_add(self, addr_id, contact_name):
        self.payload = self._customers_auth()
        self.payload.update({"addressID": addr_id})
        self.payload.update({"contact": contact_name})
        return self._dl_post(self.url_contacts_update)

    def dl_contact_update(self, person_id, contact_name):
        self.payload = self._customers_auth()
        self.payload.update({"personID": person_id})
        self.payload.update({"contact": contact_name})
        return self._dl_post(self.url_contacts_update)

    def dl_phone_add(self, addr_id, phone, add_num=None):
        self.payload = self._customers_auth()
        self.payload.update({"addressID": addr_id})
        self.payload.update({"phoneNumber": phone})
        self.payload.update({"addNumber": add_num})
        return self._dl_post(self.url_phones_update)

    def dl_phone_update(self, phone_id, phone, add_num=None):
        self.payload = self._customers_auth()
        self.payload.update({"phoneID": phone_id})
        self.payload.update({"phoneNumber": phone})
        self.payload.update({"addNumber": add_num})
        return self._dl_post(self.url_phones_update)


    def dl_any_address_add(self, params):
        """ добавление адреса, как по КЛАДР, так и произвольного
        """
        self.payload = params.copy()
        self.payload.update(self._customers_auth())
        if self.session_id:
            return self._dl_post(self.url_addresses_update)
        else:
            return self.payload


    def dl_address_add_v2(self, ca_id, free_addr):
        self.payload = self._customers_auth()
        self.payload.update({"counteragentID": ca_id})
        self.payload.update({"search": free_addr})
        return self._dl_post(self.url_addresses_update_v2)

    def dl_address_add(self, ca_id, street_kladr, house, building=None,
                       structure=None, flat=None):
        self.payload = self._customers_auth()
        self.payload.update({"counteragentID": ca_id})
        self.payload.update({"street": street_kladr})
        self.payload.update({"house": house})
        if building:
            self.payload.update({"building": building})
        if structure:
            self.payload.update({"structure": structure})
        if flat:
            self.payload.update({"flat": flat})
        return self._dl_post(self.url_addresses_update)

    def dl_address_update(self, addr_id, street_kladr=None, house=None,
                          building=None, structure=None, flat=None):
        if street_kladr is None and \
               house is None and \
               building is None and \
               structure is None and \
               flat is None:
            logging.warning('Nothing to update, all arguments are None')
            return None

        self.payload = self._customers_auth()
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

        return self._dl_post(self.url_addresses_update)

    def dl_address_term_add(self, ca_id, term_id):
        self.payload = self._customers_auth()
        self.payload.update({"counteragentID": ca_id})
        self.payload.update({"terminal_id": term_id})
        return self._dl_post(self.url_addresses_update)

    def dl_address_term_update(self, addr_id, term_id):
        self.payload = self._customers_auth()
        self.payload.update({"addressID": addr_id})
        self.payload.update({"terminal_id": term_id})
        return self._dl_post(self.url_addresses_update)

    def dl_book_delete(self, ca_list=None, addr_list=None, contact_list=None,
                       phone_list=None):
        """{
           "appkey":"00000000-0000-0000-000000000000",
           "sessionID":"00000000-0000-0000-0000-000000000000",
           "counteragents":{
              "id":[123, 345]
           },
           "addresses":{
              "id":[3,2,1]
           },
           "phones":{
              "id":[1,2]
           },
           "contacts":{
              "id":[1,2,3]
           }
        }
        """
        self.payload = self._customers_auth()
        if ca_list:
            ca_ids = dict([("id", ca_list)])
            self.payload.update({"counteragents": ca_ids})
        if addr_list:
            addr_ids = dict([("id", addr_list)])
            self.payload.update({"addresses": addr_ids})
        if phone_list:
            phone_ids = dict([("id", phone_list)])
            self.payload.update({"phones": phone_ids})
        if contact_list:
            cont_ids = dict([("id", contact_list)])
            self.payload.update({"contacts": cont_ids})
        # return self.payload
        return self._dl_post(self.url_book_delete)

    def dl_printable(self, doc_uid):
        self.payload = self._customers_auth()
        self.payload.update({"docuid": doc_uid})
        self.payload.update({"order": "bill"})
        return self._dl_post(self.url_printable)

    def dl_labels(self, order_id, shp_id, boxes):
        self.payload = self._customers_auth()
        self.payload.update({"orderID": order_id})
        self.payload.update({"cargoPlaces": [{"cargoPlace": str(shp_id), "amount": boxes}] })
        return self._dl_post(self.url_labels)

    def dl_get_labels(self, order_id, arg_format='50x80', arg_type=None):
        """ get labels
            arg_type: "pdf"-default; "jpg", "png"
            arg_format: "80x50"-default, "a4"
        """
        self.payload = self._customers_auth()
        self.payload.update({"orderID": order_id})
        self.payload.update({"type": arg_type})
        self.payload.update({"format": arg_format})
        return self._dl_post(self.url_get_labels)

    def dl_counteragents_v2(self, full_info=False):
        self.payload = self._customers_auth()
        if full_info:
            self.payload["full_info"] = str(full_info)
        return self._dl_post(self.url_counteragents_v2)

    def dl_logout(self):
        self.payload = self._customers_auth()
        return self._dl_post(self.url_logout)


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
