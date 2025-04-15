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
from app.configurations.config import DRONE_IP
from app.tasks.task_interface import TaskInterface


class CCUpdateTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone, drone_id=drone_id)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "Companion Computer Update"
        self._image_file = local_file
        self._version: str = version
        self._drone_id = drone_id
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.set_task_status(step="Uploading companion software")
        success = self._drone.cc.update_companion(self._image_file)
        return self._set_state_based_on_success(success)
