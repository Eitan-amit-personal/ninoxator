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
import logging

import dronekit

from ninox_common.log import get_logger

MAVLINK_SERIAL_BAUD_RATE = 500000
MAVLINK_HEARTBEAT_TIMEOUT_SEC = 10
__is_connected = False

logger = get_logger(__name__)


def __still_waiting_callback(atts):
    print("Still waiting for data from vehicle: %s" % ','.join(atts))


def create_vehicle_connection(connection_string, waiting_callback=__still_waiting_callback) -> dronekit.Vehicle:
    global __is_connected
    __my_vehicle = None
    logger.info("Trying to connect to vehicle")
    try:
        __my_vehicle = dronekit.connect(connection_string, wait_ready=True, still_waiting_callback=waiting_callback,
                                        heartbeat_timeout=MAVLINK_HEARTBEAT_TIMEOUT_SEC)
        ap_log = logging.getLogger('autopilot')
        ap_log.setLevel(logging.CRITICAL)
        logger.info(f"Connected to vehicle {connection_string}")
        logger.info(f"Ardupilot version {__my_vehicle.version}")
        __is_connected = True
    except dronekit.APIException:
        logger.error("Could not connect to vehicle")
        __my_vehicle = None
    except Exception as e:
        logger.error("Exception - %s", format(e))
        __my_vehicle = None

    return __my_vehicle
