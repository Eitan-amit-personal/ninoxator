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

from typing import List

from ninox_common.cc_helper import FLUTTER_SERVICE

from app.drone import Drone
from app.ingredients_echosystem.ingredients.ingredient import Ingredient
from app.tasks.task_drone_ui_flutter_update import DroneUIFlutterUpdateTask
from app.tasks.task_interface import TaskInterface
from app.tasks.task_service_deploy import ServiceDeployTask


class UiFlutterIngredient(Ingredient):
    def __init__(self, source_file_path, drone: Drone = None):
        super().__init__(drone=drone)
        self.__source_file_path = source_file_path

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug(f"UiFlutterIngredient prepare_tasks source file path={self.__source_file_path}")
        return [
            DroneUIFlutterUpdateTask(drone=self.get_drone(), local_file=self.__source_file_path),
            ServiceDeployTask(drone=self.get_drone(), service_name=FLUTTER_SERVICE,
                              service_title='Spearuav Drone UI Service',
                              working_directory='/root/drone-ui/flutter',
                              run_cmd='/usr/bin/python3 -m http.server 4010 -d /root/drone-ui/flutter')
        ]
