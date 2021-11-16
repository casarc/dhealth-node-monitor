import logging

import util.properties as prop

from node_health_monitor import DhealthNodeMonitor
from node_mining_monitor import DhealthNodeMiningMonitor

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# specify what will be the format of the logging messages
formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")

# create 2 logging handlers
# one for logging to terminal
# one for logging to file
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("health-info.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

#last thing is to add the 2 handlers to the main logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('Starting Node Health Monitor..')

    healthMonitor = DhealthNodeMonitor(prop.configs.get("node_base_url").data,
                                       eval(prop.configs.get("dhealth_node_monitor.send_notification").data))
    healthMonitor.start_monitor(int(prop.configs.get("dhealth_node_monitor.interval").data))



    mining_monitor = DhealthNodeMiningMonitor(prop.configs.get("node_base_url").data,
                                              prop.configs.get("dhealth_node_mining_monitor.reward_public_key").data,
                                              eval(prop.configs.get("dhealth_node_mining_monitor.send_notification").data))

    mining_monitor.start_monitor(int(prop.configs.get("dhealth_node_mining_monitor.interval").data))



