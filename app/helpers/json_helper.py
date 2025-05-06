#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2024
# All rights reserved.
#
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import json


def is_valid_json(json_string: str) -> bool:
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False
