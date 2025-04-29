#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
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
from app.helpers.cli_helper import drone_serial_from_user

__drone_id: int = -1
__hw_version: str = ''
__drone_type: str = ''


def get_drone_id() -> int:
    return __drone_id


def get_hw_version() -> str:
    return __hw_version


def get_drone_type() -> str:
    return __drone_type


def set_drone_id(valid_drone_id: int):
    global __drone_id
    __drone_id = valid_drone_id
    return __drone_id == valid_drone_id


def get_drone_id_from_user() -> int:
    drone_id = drone_serial_from_user()
    set_drone_id(drone_id)
    return drone_id
