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
import requests

HTTP_REQUEST_TIMEOUT_SECONDS = 10


def get_request(url, params=None, headers=None) -> requests.Response:
    try:
        response = requests.get(url, params=params, timeout=HTTP_REQUEST_TIMEOUT_SECONDS, headers=headers)
    except Exception as e:
        response = requests.Response()

    return response


def put_request(url, json=None, headers=None):
    try:
        response = requests.put(url, json=json, timeout=HTTP_REQUEST_TIMEOUT_SECONDS, headers=headers)
    except Exception as e:
        response = requests.Response()

    return response


def patch_request(url, json=None, headers=None):
    try:
        response = requests.patch(url, json=json, timeout=HTTP_REQUEST_TIMEOUT_SECONDS, headers=headers)
    except Exception as e:
        response = requests.Response()

    return response


def post_request(url, json=None, headers=None):
    try:
        response = requests.post(url, json=json, headers=headers)
    except Exception as e:
        response = requests.Response()

    return response

