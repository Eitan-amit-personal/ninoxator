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
# not a class because all methods are static
import os
import subprocess
from time import sleep, time
import requests
from http import HTTPStatus

from ninox_common.requests_wrapper import get_request, put_request, patch_request, post_request
from ninox_common.configuration import DRONE_IP

MAX_TIME_FOR_LOOP_UNTIL_SECONDS = 180
LOOP_UNTIL_SLEEP_SECONDS = 5

COMPANION_FLASK_URL = f"http://{DRONE_IP}:14010/drone"
DRONE_UI_FLASK_URL = f"http://{DRONE_IP}:5000/api/v1"
VERSIONS_COMPANION_URL = f"{DRONE_UI_FLASK_URL}/version/0"
VERSIONS_COMPANION_URL_FALLBACK = f"{DRONE_UI_FLASK_URL}/versions/companion"
CAMERA_CALIBRATION_INFO_URL = f"{COMPANION_FLASK_URL}/camera_calibration/info"
NETWORK_ID_URL = f"{DRONE_UI_FLASK_URL}/config/0/network_id"
NETWORK_ID_URL_FALLBACK = f"{DRONE_UI_FLASK_URL}/config/network_id"
DRONE_INFO_URL = f"{COMPANION_FLASK_URL}/info"
SHUTDOWN_URL = f"{COMPANION_FLASK_URL}/shutdown"


def get_camera_info():
    url = CAMERA_CALIBRATION_INFO_URL
    r = get_request(url)
    return r.json()


def patch_camera_info(json):
    r = patch_request(CAMERA_CALIBRATION_INFO_URL, json=json)
    return r.json()


def update_camera_info(camera_matrix, fovx, fovy, roll, pitch, yaw):
    """ Exception when update is unsuccessful or has non_valid_data
    :param camera_matrix:
    :param fovx:
    :param fovy:
    :param roll:
    :param pitch:
    :param yaw:
    :return: True
    """
    url = CAMERA_CALIBRATION_INFO_URL
    payload = {'calibration_status': 'calibrated', 'camera_matrix': camera_matrix, 'camera_hfov': fovx,
               'camera_vfov': fovy, 'roll': roll, 'pitch': pitch, 'yaw': yaw}
    r = put_request(url, json=payload)
    data = r.json()
    assert r.status_code == HTTPStatus.OK
    assert data["request_status"] == "successful"
    assert len(data["non_valid_data"]) == 0
    return True


def get_drone_version():
    r = get_request(DRONE_INFO_URL)
    request_data = r.json()
    return request_data["drone_version"][16:]  # remove prefix, 16 is the len of "ninox-calibration-"


def get_companion_version():
    r = get_request(VERSIONS_COMPANION_URL)
    if r.status_code != HTTPStatus.OK:
        r = get_request(VERSIONS_COMPANION_URL_FALLBACK)
    return r.json()['data']


def set_network_id(new_network_id: str) -> bool:
    headers = {"Content-Type": "application/json"}
    response = requests.put(f"{NETWORK_ID_URL}", json={'network_id': new_network_id}, headers=headers)
    if response.status_code != HTTPStatus.OK:
        response = requests.put(f"{NETWORK_ID_URL_FALLBACK}", json={'network_id': new_network_id}, headers=headers)
    return response.status_code == HTTPStatus.OK


def get_drone_id() -> int:
    """
    returns drone id or 0 if not valid
    :return:
    """
    response = get_request(f"{DRONE_INFO_URL}")
    if response.status_code == HTTPStatus.OK:
        return response.json()['serial_number']
    else:
        return 0


def get_drone_info():
    r = get_request(f"{COMPANION_FLASK_URL}/info")
    return r.json()


def get_drone_status():
    r = get_request(f"{COMPANION_FLASK_URL}/status")
    return r.json()


def get_video_stream_info():
    r = get_request(f"{COMPANION_FLASK_URL}/video_stream/info")
    return r.json()


def get_companion_configuration():  # config.ini in json
    r = get_request(f"{DRONE_UI_FLASK_URL}/config")
    return r.json()


def drone_shutdown():
    post_request(SHUTDOWN_URL)


def loop_until_drone_reachable(max_time_for_pinging_seconds=MAX_TIME_FOR_LOOP_UNTIL_SECONDS,
                               sleep_time=LOOP_UNTIL_SLEEP_SECONDS):
    return loop_until_abstract(__drone_pingable, max_time_for_pinging_seconds=max_time_for_pinging_seconds,
                               sleep_time=sleep_time)


def loop_until_api_up(max_time_for_pinging_seconds=MAX_TIME_FOR_LOOP_UNTIL_SECONDS,
                      sleep_time=LOOP_UNTIL_SLEEP_SECONDS):
    return loop_until_abstract(__api_up, max_time_for_pinging_seconds=max_time_for_pinging_seconds,
                               sleep_time=sleep_time)


def loop_until_camera_calibration_api_up(max_time_for_pinging_seconds=MAX_TIME_FOR_LOOP_UNTIL_SECONDS,
                                         sleep_time=LOOP_UNTIL_SLEEP_SECONDS):
    return loop_until_abstract(__camera_calibration_api_up, max_time_for_pinging_seconds=max_time_for_pinging_seconds,
                               sleep_time=sleep_time)


def loop_until_abstract(check_func, max_time_for_pinging_seconds=MAX_TIME_FOR_LOOP_UNTIL_SECONDS,
                        sleep_time=LOOP_UNTIL_SLEEP_SECONDS):
    start_ts = time()
    check_result_ok = False
    i = 0
    while not check_result_ok:
        if time() - start_ts > max_time_for_pinging_seconds:
            break

        if i > 0:
            sleep(sleep_time)

        try:
            check_result_ok = __call_check_func(check_func)
        except Exception as e:
            check_result_ok = False

        i += 1

    return check_result_ok


def is_pingable(ip_address: str, timeout_sec: int) -> bool:
    return __pingable(ip_address, timeout_sec)


def __call_check_func(check_func):
    try:
        check_result_ok = check_func()
    except requests.exceptions.ConnectionError as e:
        check_result_ok = False
    return check_result_ok


def __api_up():
    res = get_request(VERSIONS_COMPANION_URL)
    if res.status_code != HTTPStatus.OK:
        res = get_request(VERSIONS_COMPANION_URL_FALLBACK)
    return res.status_code == HTTPStatus.OK


def __camera_calibration_api_up():
    response = get_request(CAMERA_CALIBRATION_INFO_URL)
    return response.status_code == HTTPStatus.OK


def __drone_pingable() -> bool:
    return __pingable(DRONE_IP)


def __pingable(ip_address: str, timeout_sec: int = 1) -> bool:
    ping_timeout_ms = timeout_sec * 1000
    is_windows = os.name == 'nt'
    if is_windows:
        command = 'ping -n 1 -w {} {}'.format(ping_timeout_ms, ip_address)
    else:
        command = ['ping', '-c', '1', f'{ip_address}']

    complete_process: subprocess.CompletedProcess = None
    try:
        complete_process = subprocess.run(command, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pass

    return complete_process.returncode == 0
