#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2024
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
from app.tasks.task_mavproxy_service import MAVProxyServiceTask
from app.tasks.task_interface import TaskInterface


class MAVProxyIngredient(Ingredient):
    def __init__(self, drone: Drone = None, run_cmd: str = ''):
        super().__init__(drone=drone)
        self._run_cmd = run_cmd

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug("MAVProxyIngredient prepare_tasks")
        return self.task_with_drone(MAVProxyServiceTask, run_cmd=self._run_cmd)
