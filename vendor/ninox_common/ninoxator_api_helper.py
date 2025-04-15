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

from datetime import datetime

import requests

from ninox_common.teams_helper import send_via_notifier
from ninox_common.requests_wrapper import get_request, post_request

NINOXATOR_BACKEND_URL = "http://ec2-18-116-253-162.us-east-2.compute.amazonaws.com:3000"
NINOXATOR_POSTBACK_URL = f"{NINOXATOR_BACKEND_URL}/ninoxator"


def instance_alive() -> bool:
    # ping service by querying for a simple response
    response = requests.get(f"{NINOXATOR_BACKEND_URL}/github_releases/latest_approved_cc")
    return response.status_code // 100 == 2


def datetime_utc_now():
    return str(datetime.utcnow())


def ninoxator_postback(params, drone_id=None):
    return __ninoxator_postback_internal(params, drone_id=drone_id)


def companion_latest_approved_release_name():
    response = get_request(f"{NINOXATOR_BACKEND_URL}/github_releases/latest_approved_cc")
    return response.json()['release_name']


def log_upload_required(drone_id, uuid, closed_file):
    response = get_request(f"{NINOXATOR_BACKEND_URL}/ninoxator/log_upload_required",
                           params={'drone_id': drone_id, 'uuid': uuid, 'closed_file': closed_file})
    return response.json().get('log_upload_required', False)


def upload_companion_log(drone_id, uuid, closed_file, local_file_full_path):
    with open(local_file_full_path, 'r') as file:
        response = requests.post(f"{NINOXATOR_BACKEND_URL}/ninoxator/log_upload",
                                 params={'drone_id': drone_id, 'uuid': uuid, 'closed_file': closed_file},
                                 files={'log_file': file})
        return response.status_code // 100 == 2


def drone_file_upload_required(drone_id, uuid, file_type, closed_file):
    response = get_request(f"{NINOXATOR_BACKEND_URL}/ninoxator/drone_file_upload_required",
                           params={'drone_id': drone_id, 'uuid': uuid, 'type': file_type, 'closed_file': closed_file})
    return response.json().get('drone_file_upload_required', False)


def drone_file_upload(drone_id, uuid, file_type, closed_file, local_file_full_path, binary=False):
    open_method = 'r' if not binary else 'rb'
    with open(local_file_full_path, open_method) as file:
        response = requests.post(f"{NINOXATOR_BACKEND_URL}/ninoxator/drone_file_upload",
                                 params={'drone_id': drone_id, 'uuid': uuid, 'type': file_type,
                                         'closed_file': closed_file},
                                 files={'file': file})
        return response.status_code // 100 == 2


def add_flight(drone_id, launch_number, launch_lat, launch_lon, launch_timestamp, session_id):
    response = post_request(f"{NINOXATOR_BACKEND_URL}/flights/",
                            json={'drone_id': drone_id, 'launch_number': launch_number,
                                  'launch_location': {'lat': launch_lat, 'lon': launch_lon},
                                  'launch_timestamp': launch_timestamp, 'session_id': session_id},
                            headers={'Content-type': 'application/json', 'Accept': 'application/json'})
    return response.status_code // 100 == 2


def __ninoxator_postback_internal(params, drone_id=None):
    if not drone_id:
        drone_id = params['drone_id']
    if not drone_id:
        return False

    params_to_send = {'drone_id': drone_id}
    params_to_send.update(params)
    try:
        response = post_request(NINOXATOR_POSTBACK_URL, json=params_to_send)
        success = response.status_code // 100 == 2
    except Exception as e:
        success = False

    return success
