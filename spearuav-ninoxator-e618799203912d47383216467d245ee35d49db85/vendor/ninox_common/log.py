#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
# All rights reserved.
#
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################

import logging
from datetime import date
from logging.handlers import RotatingFileHandler

from ninox_common.configuration import LOG_FILE_DIRECTORY
from ninox_common.os_services import safe_create_folder

LOGGER_BACKUP_COUNTS = 100
LOGGER_FILE_MAX_BYTES = 20 * 1024 * 1024

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers.clear()
log_formatter = logging.Formatter('[%(asctime)s:%(msecs)03d] - %(levelname)s - %(name)6s -  %(message)s',
                                  datefmt="%d-%m-%Y %H:%M:%S")
LOG_FILENAME = f"{LOG_FILE_DIRECTORY}/{date.today()}.log"

console_log_handler = logging.StreamHandler()
console_log_handler.setLevel(logging.WARNING)
console_log_handler.setFormatter(log_formatter)
logger.addHandler(console_log_handler)

if safe_create_folder(LOG_FILE_DIRECTORY) is True:
    rot_file_handler = RotatingFileHandler(LOG_FILENAME, maxBytes=LOGGER_FILE_MAX_BYTES,
                                           backupCount=LOGGER_BACKUP_COUNTS)
    rot_file_handler.setFormatter(log_formatter)
    logger.addHandler(rot_file_handler)
    rot_file_handler.setLevel(logging.DEBUG)
    rot_file_handler.doRollover()


def get_logger(name: str):
    return logging.getLogger(name)


def disable_console_handler():
    logger.removeHandler(console_log_handler)


class Loggable:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
