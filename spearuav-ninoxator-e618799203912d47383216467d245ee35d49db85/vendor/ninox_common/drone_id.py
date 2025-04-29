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


def is_valid_drone_id(drone_id_int: int):
    try:
        allowed = drone_id_int // 1000
        if allowed < 1 or allowed > 9:
            return False

        if drone_id_int // 10000 != 0:
            return False

    except TypeError:
        return False

    return True
