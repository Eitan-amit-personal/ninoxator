#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2024
# All rights reserved.
#
# __author__ = "Tzuriel Lampner"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################

import requests

VAULT_ADDRESS = 'http://spearuav-ubuntu-server.spearuav:8020/read'


def get_secret(key: str):
    json = {"username": "", "password": ""}
    try:
        headers = {'Accept': 'application/json'}
        json = requests.get(f'{VAULT_ADDRESS}/{key}', headers=headers).json()
    except requests.exceptions.ConnectionError:
        pass
    return json

