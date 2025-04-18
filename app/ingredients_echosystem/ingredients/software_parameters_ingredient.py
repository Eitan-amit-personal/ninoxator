#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
# __author__ = "Chen Arazi"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################

from typing import List

from app.drone import Drone
from app.tasks.task_interface import TaskInterface
from app.ingredients_echosystem.ingredients.ingredient import Ingredient


class SoftwareParametersIngredient(Ingredient):
    def __init__(self, full_file_path, drone: Drone = None, drone_id=None, task=None):
        super().__init__(drone=drone)
        self.full_file_path = full_file_path
        self.drone_id = drone_id
        self.task = task

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug(f"{self.task} prepare_tasks parameters_file={self.full_file_path}")

        return self.task_with_drone(self.task, local_file=self.full_file_path,
                                    drone_id=self.drone_id)
