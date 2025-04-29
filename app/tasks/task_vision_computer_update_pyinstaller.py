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
from ninox_common.configuration import VISION_COMPUTER_IP_ADDRESS
from app.tasks.task_interface import TaskInterface


class VisionComputerUpdatePyinstallerTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone, drone_id=drone_id)
        self._prerequisite_pingable_ip = VISION_COMPUTER_IP_ADDRESS
        self._procedure_name = "Vision Computer Update"
        self._image_file = local_file
        self._version: str = version
        self._drone_id = drone_id
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        success = self._drone.vc.update_software_pyinstaller(self._image_file)
        return self._set_state_based_on_success(success)
