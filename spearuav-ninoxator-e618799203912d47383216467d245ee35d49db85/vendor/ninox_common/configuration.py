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


DRONE_IP = "192.168.137.10"
VISION_COMPUTER_IP_ADDRESS = "192.168.137.50"
LOG_FILE_DIRECTORY = "logs"
DRONE_TMP_DIR = '/tmp'
DRONE_CONFIGURATION_DIR = "/root/configuration"
DRONE_INFO_JSON = 'drone_info.json'
DRONE_CONFIG_FILE = f"{DRONE_CONFIGURATION_DIR}/{DRONE_INFO_JSON}"
EFLASH_IMAGES_FILE = "/mnt/sdcard/nanopi-neo-core-emmc.raw"
