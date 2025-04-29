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
from app.tasks.task_interface import TaskInterface
from app.tasks.task_null import NullTask


class NullIngredient(Ingredient):
    def __init__(self, full_file_path, drone: Drone = None):
        super().__init__(drone=drone)
        self.__full_file_path = full_file_path

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug("NullIngredient")
        return self.task_with_drone(NullTask, local_file=self.__full_file_path)
