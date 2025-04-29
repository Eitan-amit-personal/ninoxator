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
from app.tasks.task_drone_mcu_gimbal_update import DroneMCUGimbalUpdateTask
from app.tasks.task_interface import TaskInterface


class McuGimbalIngredient(Ingredient):
    def __init__(self, full_file_path, drone: Drone = None):
        super().__init__(drone=drone)
        self.__local_release_dir = full_file_path

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug(f"McuAttackIngredient prepare_tasks local_release_dir={self.__local_release_dir}")
        return self.task_with_drone(DroneMCUGimbalUpdateTask, local_file=self.__local_release_dir)
