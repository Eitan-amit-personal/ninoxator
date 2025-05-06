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

import dronekit

from app.tasks.task_interface import TaskInterface


class ValidateMicrohardFc(TaskInterface):
    def __init__(self, drone=None):
        super().__init__(drone=drone)
        self._procedure_name = "Validate Microhard FC"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        successful = False
        try:
            vehicle = dronekit.connect('0.0.0.0:20002', wait_ready=['system_status', 'mode', 'attitude'], rate=10,
                                       heartbeat_timeout=7)
            vehicle.close()
            successful = True
        except Exception as e:
            self._errors.append(f"Got exception: {e} ")

        return self._set_state_based_on_success(successful)
