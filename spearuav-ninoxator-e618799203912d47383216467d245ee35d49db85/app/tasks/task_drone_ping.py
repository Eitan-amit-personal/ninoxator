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
from ninox_common.drone_api_helper import loop_until_drone_reachable

from app.tasks.task_interface import TaskInterface

PING_TIMEOUT_SEC = 60


class DronePingTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = ''
        self._prerequisite_drone_id = False
        self._procedure_name = "Wait for Drone Pingable"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("DronePing go")
        result = loop_until_drone_reachable(max_time_for_pinging_seconds=PING_TIMEOUT_SEC)
        return self._set_state_based_on_success(result)
