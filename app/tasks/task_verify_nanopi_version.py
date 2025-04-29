#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2024
# All rights reserved.
#
# __author__ = "Tzuriel Lampner"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
from ninox_common.cc_helper import CCHelper

from app.configurations.config import DRONE_IP
from app.tasks.task_interface import TaskInterface


class NanopiVersionVerifyTask(TaskInterface):
    def __init__(self, drone=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._prerequisite_drone_id = False
        self._procedure_name = "Verify NanoPi Linux Version 20.04"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("Verify NanoPi Firmware Version")
        my_helper = CCHelper()
        result = "20.04" in my_helper.linux_version()
        return self._set_state_based_on_success(result)
