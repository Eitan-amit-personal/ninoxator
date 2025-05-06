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

from ninox_common.cc_helper import COMPANION_SERVICE

from app.drone import Drone
from app.ingredients_echosystem.ingredients.ingredient import Ingredient
from app.tasks.task_cc_update import CCUpdateTask
from app.tasks.task_interface import TaskInterface
from app.tasks.task_nanopi_rules import NanoPiRulesDeployTask
from app.tasks.task_service_deploy import ServiceDeployTask


class CCIngredient(Ingredient):
    def __init__(self, full_file_path, version, drone: Drone = None):
        super().__init__(drone=drone)
        self.__local_release_dir = full_file_path
        self.__companion_version = version

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug(f"CCIngredient prepare_tasks local_release_dir={self.__local_release_dir}")
        return [
            CCUpdateTask(drone=self.get_drone(),
                         local_file=self.__local_release_dir,
                         version=self.__companion_version),
            ServiceDeployTask(drone=self.get_drone(), service_name=COMPANION_SERVICE,
                              service_title='Spearuav Drone Companion Service',
                              working_directory='/root/companion',
                              run_cmd='python3 run.py',
                              delay_sec=30),
            NanoPiRulesDeployTask(drone=self.get_drone())
        ]
