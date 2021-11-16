from typing import *

import requests
import logging

class DhealthNodeClient:
    def __init__(self, node_base_url: str):
        self._dhealth_node_base_url = node_base_url


    # define private method called for making http requests to the DhealthClient api
    def _make_request(self, endpoint: str, query_parameters: Dict):
        try:
            response = requests.get(self._dhealth_node_base_url + endpoint, params=query_parameters)
        except Exception as e:
            logging.error("Connection error while making request to %s, %s", endpoint, e)
            return None

        if response.status_code == 200:
            return response.json()
        else:
            logging.error("Error while making request to %s: %s (status code = %s)",
                         endpoint, response.json(), response.status_code)
            return None


    def get_accounts(self, public_key:str)->str:
        params = dict()
        url =  "/accounts" + "/" + public_key
        response = self._make_request(url, params)
        return response

    def get_accounts_amount(self, public_key: str) -> int:
        account_info = self.get_accounts(public_key)
        mosaics = account_info['account']['mosaics']
        total_amount = 0.0
        for item in mosaics:
            total_amount = total_amount + int(item['amount'])

        return total_amount
