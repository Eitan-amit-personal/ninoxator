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

import subprocess

from app.configurations.config import NINOX_CALIBRATION_RUN
from app.tasks.task_interface import TaskInterface


class NinoxCalibration(TaskInterface):
    def __init__(self, drone=None):
        super().__init__(drone=drone)
        self._with_halo = False  # this task has prints so no Halo.
        self._procedure_name = "Ninox Calibration"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("NinoxCalibration go")
        exit_status_code = subprocess.call(NINOX_CALIBRATION_RUN, shell=True)
        return self._set_state_based_on_success(exit_status_code == 0)
