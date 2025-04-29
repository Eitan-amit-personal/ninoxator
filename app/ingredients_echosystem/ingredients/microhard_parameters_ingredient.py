#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
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

from typing import List

from app.drone import Drone
from app.ingredients_echosystem.ingredients.ingredient import Ingredient
from app.tasks.microhard import MicrohardParameters
from app.tasks.task_interface import TaskInterface


class MicrohardParametersIngredient(Ingredient):
    def __init__(self, full_file_path, drone: Drone = None):
        super().__init__(drone=drone)
        self.__full_file_path = full_file_path

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug(f"MicrohardParametersIngredient prepare_tasks firmware_file={self.__full_file_path}")
        return self.task_with_drone(MicrohardParameters, microhard_parameters_file=self.__full_file_path)
