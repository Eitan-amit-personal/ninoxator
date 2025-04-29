#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
# __author__ = "Tzuriel Lampner"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################

from app.configurations.config import VISION_COMPUTER_IP_ADDRESS
from app.tasks.task_interface import TaskInterface


class CleanServicesTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = VISION_COMPUTER_IP_ADDRESS
        self._procedure_name = "Clean unnecessary services"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("CleanServicesTask go")
        success = True
        self.set_task_status(step="Removing old services")
        success = success and self._drone.vc.remove_drone_ui_flask_service()
        return self._set_state_based_on_success(success)
