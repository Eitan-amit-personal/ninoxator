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
from ninox_common.cc_helper import CCHelper

from app.configurations.config import DRONE_IP
from app.helpers.cli_helper import print_error
from app.tasks.task_interface import TaskInterface


class CCFlashTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__()
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "Companion Computer Flash"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.set_task_status(step="Flashing")
        cc_helper = CCHelper()
        result = False
        if not cc_helper.is_eflasher():
            print_error("\nNo flashing SD card in NanoPI")
        else:
            result = cc_helper.flash_companion()
        return self._set_state_based_on_success(result)
