""""
Configures the log for the application. We added a distinct logger.yaml file to configure the log, because we want
to use a distinct logger for the data generator app.

@author: Adrian
"""

import logging.config
import yaml


def config():
    """
    Configures the log for the application. The configuration is read from the logger.yaml file
    """
    with open("./config/logger.yaml") as f:
        config_obj = yaml.safe_load(f)
        logging.config.dictConfig(config_obj)
