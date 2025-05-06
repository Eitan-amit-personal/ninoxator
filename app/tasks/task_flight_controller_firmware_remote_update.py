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
from app.helpers.debug_helper import verbose_mode


class FlightControllerRemoteFirmwareUpdateTask(TaskInterface):

    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self.firmware_file = local_file
        self.port = None
        self._version = None
        self._prerequisite_pingable_ip = DRONE_IP
        self.connection_string = None
        self._procedure_name = "Flight Controller Remote Firmware Update"
        self.set_task_status_ready()

    @property
    def version(self):
        return self._version

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.set_task_status(step="Updating flight controller firmware")
        result = self.get_drone().cc.update_ardupilot_firmware(self.firmware_file, verbose_mode())
        return self._set_state_based_on_success(result)
