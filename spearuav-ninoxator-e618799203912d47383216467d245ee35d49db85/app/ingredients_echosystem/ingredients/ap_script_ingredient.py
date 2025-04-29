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
from app.tasks.task_ap_lua_script import ArdupilotLuaScriptTask


class ArdupilotLuaScriptIngredient(Ingredient):
    def __init__(self, source_file_path, version, drone: Drone = None):
        super().__init__(drone=drone)
        self.__script = source_file_path
        self.__version = version

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.debug(f"ArdupilotLuaScriptIngredient prepare_tasks script = {self.__script} {self.__version}")
        return self.task_with_drone(ArdupilotLuaScriptTask, local_file=self.__script, version=self.__version)
