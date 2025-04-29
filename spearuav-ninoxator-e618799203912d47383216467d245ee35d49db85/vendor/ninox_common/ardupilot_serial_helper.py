#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2022
# All rights reserved.
#
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################

import serial
import serial.tools.list_ports
from ninox_common.log import get_logger

logger = get_logger(__name__)

ardupilot_ports: set = {'ArduPilot', 'MatekH743', 'mRoControlZeroOEMH7'}


def ports_to_try(ports_filter: set = None, black_ports=None) -> list:
    if ports_filter is None:
        ports_filter = ardupilot_ports
    if black_ports is None:
        black_ports = []
    portlist = []
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        skip = False
        for black_port in black_ports:
            if black_port in desc:
                skip = True
                break
        for candidate_port in ports_filter:
            if candidate_port in desc and skip is False:
                portlist.append(port)
                logger.debug(f'{port}: {desc} [{hwid}]')

    return portlist
