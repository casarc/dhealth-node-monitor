from typing import *
from dhealth_node.dhealth_client import DhealthNodeClient
from notification.telegram_notification import TelegramNotification

from datetime import datetime

import logging
import requests

import time
import threading

import util.properties as prop

logger = logging.getLogger()

class DhealthNodeMonitor:
    def __init__(self, base_url : str, send_notification: bool):
        self._base_url = base_url
        self._monitor = False
        self._send_notification = send_notification

        self._occamnautsClient = DhealthNodeClient(self._base_url)

        self._current_api_node_status = None
        self._current_db_status = None

        self._telegram_client = TelegramNotification(prop.configs.get("telegram.api_id").data,
                                                     prop.configs.get("telegram.api_hash").data,
                                                     prop.configs.get("telegram.bot_token").data)

        self._chat_id = int(prop.configs.get("telegram.chat_id").data)



    """
    monitor the dhealth node at regular time interval set by interval_millis
    """
    # define private method called for making http requests to the Binance api
    def _make_request(self, endpoint: str, query_parameters: Dict) -> str:
        try:
            response = requests.get(self._base_url + endpoint,  params=query_parameters)
        except Exception as e:
            logger.error("Connection error while making request to %s, %s", endpoint, e)
            return None

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making request to %s: %s (status code = %s)",
                         endpoint, response.json(), response.status_code)
            return None

    """
    obtain the node heath json data from node end point
    """
    def _check_node_health(self):
        #logging.info("_check_node_health::thread =%s", threading.currentThread().getName())
        now = datetime.now() # current date and time
        date_time_str = now.strftime("%d/%m/%Y-%H:%M:%S")

        params = dict()
        endpoint = "/node/health"
        status_data = self._make_request(endpoint, params)

        # {'status': {'apiNode': 'up', 'db': 'up'}}
        api_status = status_data['status']['apiNode']
        db_status = status_data['status']['db']

        _status_change = False
        _status_message: str = "Status Update: " + date_time_str + "\n"

        if self._current_api_node_status != api_status:
            _status_message = _status_message + "[api_status=" +  api_status + "]" + "\n"
            self._current_api_node_status = api_status
            _status_change = True

        if self._current_db_status != db_status:
            _status_message = _status_message + "[db_status=" +  db_status + "]"
            self._current_db_status = db_status
            _status_change = True

        if _status_change:
            logger.info(_status_message)
            if self._send_notification:
                self._telegram_client.send_message(self._chat_id,_status_message)



    """
    kick off the monitor thread 
    """
    def start_monitor(self, interval_sec: int):
        logging.info("DhealthNodeMonitor::start_monitor - thread =%s", threading.currentThread().getName())
        self._monitor = True
        threading.Thread(target=lambda: self._every(interval_sec, self._check_node_health)).start()

    def stop_monitor(self):
        self._monitor = True

    def _every(self, delay: int, task):
        next_time = time.time() + delay
        while self._monitor:
            sleep_amount = next_time - time.time()
            time.sleep(max(0, sleep_amount))
            try:
                task()
            except Exception as e:
                logging.error("DhealthNodeMonitor::Error Occurred in _every(): %s", e)

            # skip tasks if we are behind schedule:
            next_time += (time.time() - next_time) // delay * delay + delay
        logging.info("_every::exit")
