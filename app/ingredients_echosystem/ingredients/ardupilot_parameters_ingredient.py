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
from app.tasks.task_flight_controller_parameters import FlightControllerParametersUpdateTask
from app.tasks.task_interface import TaskInterface


class ArdupilotParametersIngredient(Ingredient):
    def __init__(self, full_file_path, drone: Drone = None, drone_id=None):
        super().__init__(drone=drone)
        self.full_file_path = full_file_path
        self.drone_id = drone_id

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug(f"ArdupilotParametersIngredient prepare_tasks parameters_file={self.full_file_path}")

        return self.task_with_drone(FlightControllerParametersUpdateTask, local_file=self.full_file_path,
                                    drone_id=self.drone_id)
