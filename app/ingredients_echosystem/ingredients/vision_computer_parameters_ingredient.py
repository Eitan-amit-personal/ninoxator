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
from app.ingredients_echosystem.ingredients.software_parameters_ingredient import SoftwareParametersIngredient
from app.tasks.task_interface import TaskInterface
from app.tasks.task_jetson_rules import JetsonRulesDeployTask
from app.tasks.task_vision_computer_parameters import VisionComputerParametersUpdateTask


class VisionComputerParametersIngredient(SoftwareParametersIngredient):
    def __init__(self, full_file_path, drone: Drone = None, drone_id=None):
        super().__init__(drone=drone, full_file_path=full_file_path, drone_id=drone_id)

    def prepare_tasks(self) -> List[TaskInterface]:
        return [
            VisionComputerParametersUpdateTask(
                drone=self.get_drone(),
                drone_id=self.drone_id,
                local_file=self.full_file_path),
            JetsonRulesDeployTask(drone=self.get_drone())
        ]
