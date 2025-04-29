#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2024
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

from typing import List

from app.drone import Drone
from app.ingredients_echosystem.ingredients.ingredient import Ingredient
from app.tasks.task_app_deploy import AppDeployTask
from app.tasks.task_service_deploy import ServiceDeployTask
from app.tasks.task_interface import TaskInterface

from ninox_common.cc_helper import TELEMETRY_SERVICE


class TelemetryIngredient(Ingredient):
    def __init__(self, source_file_path, run_cmd: str, drone: Drone = None):
        super().__init__(drone=drone)
        self.__source_file_path = source_file_path
        self._run_cmd = run_cmd

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug("TelemetryIngredient prepare_tasks")
        return [
            AppDeployTask(drone=self.get_drone(),
                          binary=self.__source_file_path,
                          working_folder='/root'),
            ServiceDeployTask(drone=self.get_drone(),
                              service_name=TELEMETRY_SERVICE,
                              service_title='Spearuav Drone Telemetry Service',
                              working_directory='/root',
                              run_cmd='/root/serial_to_udp ' + self._run_cmd,
                              enabled=False)    # Since it's only used for tests, disabled by default
        ]
