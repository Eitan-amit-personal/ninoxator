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

from app.drone import Drone
from app.ingredients_echosystem.ingredients.software_parameters_ingredient import SoftwareParametersIngredient
from app.tasks.task_companion_computer_parameters import CompanionComputerParametersUpdateTask


class CompanionComputerParametersIngredient(SoftwareParametersIngredient):
    def __init__(self, full_file_path, drone: Drone = None, drone_id=None):
        super().__init__(drone=drone, full_file_path=full_file_path, drone_id=drone_id,
                         task=CompanionComputerParametersUpdateTask)
