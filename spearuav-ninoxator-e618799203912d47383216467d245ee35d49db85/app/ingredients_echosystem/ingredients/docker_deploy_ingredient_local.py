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
from app.tasks.task_docker_deploy_local import DockerDeployLocalTask
from app.tasks.task_interface import TaskInterface


class DockerDeployLocalIngredient(Ingredient):
    def __init__(self, source_file_path, container_url, version, drone: Drone = None, run_cmd=''):
        super().__init__(drone=drone)
        self.__container = source_file_path  # the path to the docker tar gzi
        self.__container_url = container_url
        self.__version = version
        self._run_cmd = run_cmd

    def prepare_tasks(self) -> List[TaskInterface]:
        self.logger.info(
            f"DockerDeployIngredient prepare_tasks container = {self.__container} from {self.__container_url} {self.__version} {self._run_cmd}")
        return self.task_with_drone(
            DockerDeployLocalTask, local_file=self.__container, version=self.__version, run_cmd=self._run_cmd, container_url=self.__container_url)
