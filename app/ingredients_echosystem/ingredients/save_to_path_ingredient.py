#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2025
# All rights reserved.
#
# __author__ = "Eitan Amit"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import os
from app.drone import Drone
from app.ingredients_echosystem.ingredients.ingredient import Ingredient
from app.tasks.task_interface import TaskInterface
from typing import List


class SaveParameterToPathIngredient(Ingredient):
    def __init__(self, source_file_path: str, drone: Drone, target_path: str):
        super().__init__(drone=drone)
        self._source = source_file_path
        self._target_path = target_path

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.info(f"Saving {self._source} to {self._target_path} on drone {self.drone.ip}")
        if not os.path.exists(self._source):
            self.logger.error(f"Source file does not exist: {self._source}")
            raise FileNotFoundError(self._source)

        # Use SCP via drone.upload_file helper
        self.drone.upload_file(self._source, self._target_path)
        return []
