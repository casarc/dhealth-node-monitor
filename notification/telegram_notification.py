# importing all required libraries
from typing import *

import requests
import logging

class TelegramNotification:
    def __init__(self, api_id: int, api_hash: str, bot_token: str):
        # get your api_id, api_hash, token
        # from telegram as described above
        self.api_id = api_id
        self.api_hash = api_hash
        self.token = 'bot token'
        self.message = None

        self.telegram_base_url = "https://api.telegram.org"
        self.bot_token = bot_token

    def send_message(self, chat_id: int, msg: str):
        logging.info("sending notification, message=%s", msg)
        try:
            query_parameters: Dict = dict()
            query_parameters['chat_id'] = chat_id
            query_parameters['text'] = msg

            post_url = self.telegram_base_url + "/bot" + self.bot_token + "/sendMessage"

            #response = None
            response = requests.post(post_url, data=query_parameters)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error("Error while making request to %s: %s (status code = %s)",
                              post_url, response.json(), response.status_code)
            return None
        except Exception as e:
            logging.error("error occurred in send_message %s", e)
