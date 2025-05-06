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


class DroneUIFlutterUpdateTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "Drone-UI-Flutter"
        self._local_image_file = local_file
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("DroneUIFlutterUpdateTask go")
        self.set_task_status(step="Uploading flutter package")
        status = self.get_drone().cc.update_drone_ui_flutter(self._local_image_file)
        return self._set_state_based_on_success(status)
