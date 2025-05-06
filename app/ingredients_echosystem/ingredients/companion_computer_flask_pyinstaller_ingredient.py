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

from app.drone import Drone
from app.ingredients_echosystem.ingredients.ingredient import Ingredient
from app.tasks.task_app_deploy import AppDeployTask
from app.tasks.task_interface import TaskInterface
from app.tasks.task_service_deploy import ServiceDeployTask

from ninox_common.cc_helper import FLASK_SERVICE_PYINSTALLER, FLASK_SERVICE_OLD


class CompanionComputerFlaskPyinstallerIngredient(Ingredient):
    def __init__(self, source_file_path, run_cmd: str, drone: Drone = None):
        super().__init__(drone=drone)
        self.__source_file_path = source_file_path
        self._run_cmd = run_cmd

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug(
            f"CompanionComputerFlaskPyinstallerIngredient prepare_tasks source file path={self.__source_file_path}")
        return [
            AppDeployTask(drone=self.get_drone(),
                          binary=self.__source_file_path,
                          working_folder='/root/drone-ui/flask'),
            ServiceDeployTask(drone=self.get_drone(),
                              service_name=FLASK_SERVICE_PYINSTALLER,
                              remove_service_name=FLASK_SERVICE_OLD,
                              service_title='Spearuav Drone UI Flask Service',
                              working_directory='/root/drone-ui/flask',
                              run_cmd='/root/drone-ui/flask/drone-ui-flask-nanopi ' + self._run_cmd)
        ]
