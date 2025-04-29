# !/usr/bin/env python
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

import datetime

NINOX_PRODUCTION_STATION_SOFTWARE_VERSION = "${VERSION}"


def get_version():
    if "{VERSION}" not in NINOX_PRODUCTION_STATION_SOFTWARE_VERSION:
        return NINOX_PRODUCTION_STATION_SOFTWARE_VERSION
    else:
        return f'ninoxator-development-version-{datetime.datetime.now().strftime("%d%m%Y-%H%M%S")}'
