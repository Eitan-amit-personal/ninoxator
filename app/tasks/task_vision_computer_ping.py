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
from ninox_common.drone_api_helper import is_pingable

from app.configurations.config import VISION_COMPUTER_IP_ADDRESS
from app.tasks.task_interface import TaskInterface

PING_TIMEOUT_SEC = 60


class VisionComputerPingTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = ''
        self._prerequisite_drone_id = False
        self._procedure_name = "Vision Computer Pingable"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("Vision Computer Ping go")
        result = is_pingable(VISION_COMPUTER_IP_ADDRESS, timeout_sec=PING_TIMEOUT_SEC)
        return self._set_state_based_on_success(result)
