#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
# __author__ = "Chen Arazi"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################

from app.tasks.task_interface import TaskInterface


class VisionComputerParametersUpdateTask(TaskInterface):

    def __init__(self, drone=None, drone_id=None, local_file=None):
        super().__init__(drone=drone, drone_id=drone_id)
        self._prerequisite_drone_id = True
        self._procedure_name = "Vision Computer Parameters"
        self._local_file = local_file
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        status = True
        self.set_task_status(step="Uploading parameters file")
        status = status and self._drone.vc.update_vision_computer_parameters(self._local_file)
        self.set_task_status(step="Signing file (update hash)")
        status = status and self._drone.vc.sign_config_file_hash()
        return self._set_state_based_on_success(status)
