from typing import *
from datetime import datetime
from dhealth_node.dhealth_client import DhealthNodeClient
from notification.telegram_notification import TelegramNotification

import logging
import util.properties as prop

import time
import threading

logger = logging.getLogger()

class DhealthNodeMiningMonitor:
    def __init__(self, base_url : str, account_pub_key: str, send_notification: bool):
        self._base_url = base_url
        self._monitor = False

        self._send_notification = send_notification

        self._dhealth_node_client = DhealthNodeClient(self._base_url)

        self._reward_public_key = account_pub_key

        self._current_mining_reward_balance = 0

        self._telegram_client = TelegramNotification(prop.configs.get("telegram.api_id").data,
                                                     prop.configs.get("telegram.api_hash").data,
                                                     prop.configs.get("telegram.bot_token").data)

        self._chat_id = int(prop.configs.get("telegram.chat_id").data)

    def _publish_node_mining_rewards(self):
        now = datetime.now()
        date_time_str = now.strftime("%d/%m/%Y-%H:%M:%S")
        _status_message: str = "Status Update: " + date_time_str + "\n"

        _mining_rewards_balance = self._dhealth_node_client.get_accounts_amount(self._reward_public_key)
        _mining_rewards_balance = _mining_rewards_balance / 1000000
        if self._current_mining_reward_balance != _mining_rewards_balance:
            _status_message = _status_message + "[Mining Rewards=" + str(_mining_rewards_balance) + "]" + "\n"
            logger.info(_status_message)
            self._current_mining_reward_balance = _mining_rewards_balance

            if self._send_notification:
                self._telegram_client.send_message(self._chat_id, _status_message)



    """
    kick off the monitor thread 
    """
    def start_monitor(self, interval_sec: int):
        logging.info("DhealthNodeMiningMonitor::start_monitor - thread =%s", threading.currentThread().getName())
        self._monitor = True
        threading.Thread(target=lambda: self._every(interval_sec, self._publish_node_mining_rewards)).start()

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
                logging.error("Error Occurred in _every(): %s", e)

            # skip tasks if we are behind schedule:
            next_time += (time.time() - next_time) // delay * delay + delay
        logging.info("_every::exit")
