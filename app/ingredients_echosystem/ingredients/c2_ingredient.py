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
from app.tasks.task_interface import TaskInterface


class C2Ingredient(Ingredient):
    def __init__(self, drone: Drone, source_file_path: str):
        super().__init__(drone=drone)
        self.__source_file_path = source_file_path

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug("C2Ingredient prepare_tasks")
        return self.task_with_drone(AppDeployTask, binary=self.__source_file_path, working_folder='/root/c2')
