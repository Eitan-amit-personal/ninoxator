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
import os

from app.configurations.config import DRONE_IP
from app.tasks.task_interface import TaskInterface


class AppDeployTask(TaskInterface):
    def __init__(self, drone=None, binary='', working_folder=''):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = f"App Deploy Task - {os.path.basename(binary)}"
        self._binary = binary
        self._working_folder = working_folder
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("AppDeployTask - go")

        self.set_task_status(step="Uploading binary")
        self._drone.cc.upload_file(self._binary, self._working_folder)

        return self._set_state_based_on_success(True)
