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
import pathlib

from app.configurations.config import DRONE_IP
from app.tasks.task_interface import TaskInterface
from app.helpers.debug_helper import verbose_mode

current_path = str(pathlib.Path(__file__).parent.resolve())
LOCAL_UTILITY_DIR = pathlib.Path(current_path + '/../utilities/arm32/')


class DroneMCUAttackUpdateTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "Drone-MCU-Attack"
        self._local_image_file = local_file
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("DroneMCUAttackUpdateTask go")
        self.set_task_status(step="Uploading MCU hex file")
        status = self.get_drone().cc.update_mcu_attack(LOCAL_UTILITY_DIR, self._local_image_file, verbose_mode())
        return self._set_state_based_on_success(status)
