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

from app.configurations.config import DRONE_IP
from app.tasks.task_interface import TaskInterface


class GetDroneIdInDroneInfoTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None, set_drone_id_func=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "Get Drone ID from Drone Info"
        self.set_task_status_ready()
        self._drone_id = -1
        self._drone_id_setter = set_drone_id_func

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("GetDroneIdInDroneInfo go")
        self._drone_id = self.get_drone().cc.get_drone_id_from_drone_info()
        status = self._drone_id != -1
        if status and self._drone_id_setter is not None:
            self._drone_id_setter(self._drone_id)
        return self._set_state_based_on_success(status)

    @property
    def drone_id(self):
        return self._drone_id
