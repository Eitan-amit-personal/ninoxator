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
import os


def safe_create_folder(folder_name) -> bool:
    folder = os.path.normpath(folder_name)
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except PermissionError:
            return False

    return True
