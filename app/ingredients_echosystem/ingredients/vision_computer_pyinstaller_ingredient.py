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
from app.tasks.task_interface import TaskInterface
from app.tasks.task_vision_computer_update_pyinstaller import VisionComputerUpdatePyinstallerTask


class VisionComputerPyinstallerIngredient(Ingredient):
    def __init__(self, full_file_path, version, drone: Drone = None):
        super().__init__(drone=drone)
        self.__local_release_dir = full_file_path
        self.__vision_computer_version = version

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug(f"VisionComputerIngredient prepare_tasks local_release_dir={self.__local_release_dir}")
        return self.task_with_drone(VisionComputerUpdatePyinstallerTask, local_file=self.__local_release_dir,
                                    version=self.__vision_computer_version)
