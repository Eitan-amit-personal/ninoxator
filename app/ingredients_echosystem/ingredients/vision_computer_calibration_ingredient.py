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
from app.tasks.task_interface import TaskInterface
from app.tasks.task_vision_computer_camera_calibration_update import VisionComputerCameraCalibrationUpdateTask


class VisionComputerCalibrationIngredient(Ingredient):
    def __init__(self, full_file_path, drone: Drone = None):
        super().__init__(drone=drone)
        self.__full_file_path = full_file_path

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug(f"VisionComputerCalibrationIngredient prepare_tasks {self.__full_file_path}")
        return self.task_with_drone(VisionComputerCameraCalibrationUpdateTask, local_file=self.__full_file_path)
