#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
# All rights reserved.
#
# __author__ = "Idan Levinson"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import os
from pathlib import Path
import configparser
import ninox_common.configuration
from ninox_common.configuration import VISION_COMPUTER_IP_ADDRESS

from app.configurations.config_linux import LINUX_KEY_PATH, LINUX_FC_CONNECTION_STRING_BEGINNING, \
    LINUX_EMPTY_GIT_CACHE, LINUX_COMPANION_RELEASES_DIR
from app.configurations.config_windows import WIN_KEY_PATH, WIN_FC_CONNECTION_STRING_BEGINNING, WIN_EMPTY_GIT_CACHE, \
    WIN_COMPANION_RELEASES_DIR

win = os.name == 'nt'

PROJECT_DIRECTORY = Path(__file__).parent.parent.parent
CONNECTION_STRING = "0.0.0.0:20002"
GIT_LOCAL_DIRECTORY = "app/from_git"
KEY_PATH = WIN_KEY_PATH if win else LINUX_KEY_PATH
DRONE_IP = ninox_common.configuration.DRONE_IP
EFLASH_DIRECTORY = f"{PROJECT_DIRECTORY}/app/tasks/eflash/"
FC_CONNECTION_STRING_BEGINNING = WIN_FC_CONNECTION_STRING_BEGINNING if win else LINUX_FC_CONNECTION_STRING_BEGINNING
EMPTY_GIT_CACHE = WIN_EMPTY_GIT_CACHE if win else LINUX_EMPTY_GIT_CACHE
COMMUNICATION_DEVICE_IP = "192.168.137.33"
NINOX_CALIBRATION_RUN = f"{PROJECT_DIRECTORY}/../ninox_calibration/run.py"
DRONE_ASSESTS_DIR = "app/drone_assets"
COMPANION_RELEASES_DIR = WIN_COMPANION_RELEASES_DIR if win else LINUX_COMPANION_RELEASES_DIR
NETWORK_ID_PREFIX = "ninox_"
DRONE_FLASK_URL = f"http://{DRONE_IP}:5000/api/v1"
DRONE_FLASK_CONFIG_URL = f"{DRONE_FLASK_URL}/config"
DRONE_FLASK_CONFIG_PYINSTALLER_URL: str = f"{DRONE_FLASK_URL}/config/0"
VISION_FLASK_URL = f"http://{VISION_COMPUTER_IP_ADDRESS}:4000/api/v1"
VISION_FLASK_CONFIG_URL = f"{VISION_FLASK_URL}/config/1"
COMPANION_LOGS_DIR = 'companion/logs'
COOKING_ASSETS_DIR = 'app/cooking_assets'

CONFIG_FILE = "app/configurations/config.ini"
LOCAL_FLASHING = "LOCAL_FLASHING"

_config = configparser.ConfigParser()
_config.read(CONFIG_FILE)


def read_versions_directory() -> str:
    global _config
    return _config.get(LOCAL_FLASHING, "packed_versions_dir", fallback=False)
