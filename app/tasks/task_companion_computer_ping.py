#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
# __author__ = "Roie Geron"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import time
import ninox_common.ssh_helper as ssh_helper
import ninox_common.cc_helper as cc_helper
from ninox_common.drone_api_helper import is_pingable

from app.configurations.config import DRONE_IP
from app.tasks.task_interface import TaskInterface

PING_TIMEOUT_SEC = 5


class CompanionComputerPingTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = ''
        self._prerequisite_drone_id = False
        self._procedure_name = "Companion Computer Pingable"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("Companion Computer Ping go")
        result = is_pingable(DRONE_IP, timeout_sec=PING_TIMEOUT_SEC)
        result = result and self.can_log_into_nanopi()
        return self._set_state_based_on_success(result)

    def can_log_into_nanopi(self, timeout_sec=PING_TIMEOUT_SEC) -> bool:
        start = time.time()
        while time.time() < start + timeout_sec:
            ssh = ssh_helper.SSHHelper(cc_helper.DRONE_IP, cc_helper.USERNAME, cc_helper.PASSWORD)
            ssh.open_session()
            is_active = ssh.ssh_is_active()
            del ssh
            if is_active:
                return True

        return False
