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

from app.tasks.task_interface import TaskInterface


class DroneIdFcParamTask(TaskInterface):
    def __init__(self, drone=None):
        super().__init__(drone=drone)
        self._prerequisite_drone_id = True
        self._prerequisite_flight_controller_firmware = True
        self._procedure_name = "Set Drone ID in Flight Controller"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("DroneIdFcParam go")
        success = False
        try:
            self.get_drone().set_drone_id_in_fc()
            success = True
        except Exception as e:
            self._errors.append(e)
            success = False

        return self._set_state_based_on_success(success)
