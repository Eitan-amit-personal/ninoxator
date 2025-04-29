#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
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


class ArdupilotDeviceExistTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._prerequisite_drone_id = False
        self._procedure_name = "Ardupilot Device exist"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("Ardupilot Device exist go")
        my_helper = CCHelper()
        result = my_helper.is_mcu_ardupilot_device_exists()
        return self._set_state_based_on_success(result)
