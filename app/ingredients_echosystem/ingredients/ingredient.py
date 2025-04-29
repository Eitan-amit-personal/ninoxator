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

from ninox_common.log import Loggable

from app.drone import Drone
from app.tasks.task_interface import TaskInterface


class Ingredient(Loggable):
    def __init__(self, drone: Drone = None):
        super().__init__()
        self._drone = drone

    def get_drone(self):
        return self._drone

    def prepare_tasks(self) -> List[TaskInterface]:
        raise NotImplementedError

    def task_with_drone(self, task_class_name, **kwargs):
        return [task_class_name(drone=self.get_drone(), **kwargs)]
