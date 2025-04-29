#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
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


class SetDroneVersionsInDroneInfoTask(TaskInterface):
    def __init__(self, drone_id, drone=None, version=None, local_file=None, hw_version=None, drone_type=None):
        super().__init__(drone=drone, drone_id=drone_id)
        self._prerequisite_pingable_ip = DRONE_IP
        self._prerequisite_drone_id = False
        self._procedure_name = "Set Drone ID in Drone Info"
        self.set_task_status_ready()
        self.version = version
        self.hw_version = hw_version
        self.drone_type = drone_type

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("SetDroneVersionsInDroneInfoTask go")
        self._drone.cc.set_drone_info(drone_id=self._drone_id,
                                      software_version=self.version,
                                      hw_version=self.hw_version,
                                      drone_type=self.drone_type)
        current_drone_id = self._drone.cc.get_drone_id_from_drone_info()
        return self._set_state_based_on_success(current_drone_id == self._drone_id)
