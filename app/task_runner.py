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

def execute_task(task_class, drone, drone_id=None, local_file=None, version=None, **kwargs) -> bool:
    my_task = task_class(drone=drone, drone_id=drone_id, local_file=local_file, version=version, **kwargs)
    status = my_task.prerequisites()
    if status is True:
        status = my_task.go()

    return status
