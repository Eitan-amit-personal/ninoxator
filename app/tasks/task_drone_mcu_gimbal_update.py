#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
# __author__ = "Roie Geron"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import pathlib

from app.configurations.config import VISION_COMPUTER_IP_ADDRESS
from app.tasks.task_interface import TaskInterface
from app.helpers.debug_helper import verbose_mode


current_path = str(pathlib.Path(__file__).parent.resolve())
LOCAL_UTILITY_DIR = pathlib.Path(current_path + '/../utilities/arm64/')


class DroneMCUGimbalUpdateTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = VISION_COMPUTER_IP_ADDRESS
        self._procedure_name = "Drone-MCU-Gimbal"
        self._local_image_file = local_file
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("DroneMCUGimbalUpdateTask go")
        status = self.get_drone().vc.update_mcu_gimbal(LOCAL_UTILITY_DIR, self._local_image_file, verbose_mode())
        return self._set_state_based_on_success(status)
