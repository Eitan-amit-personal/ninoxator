#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
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
from app.configurations.config import VISION_COMPUTER_IP_ADDRESS

from app.tasks.task_interface import TaskInterface


class VisionComputerDockerClearTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = VISION_COMPUTER_IP_ADDRESS
        self._prerequisite_drone_id = False
        self._procedure_name = "VC Docker Clear Task"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("VC Docker Clear Task - go")
        # stop and remove all containers
        self._drone.vc.ssh_exec('docker stop $(docker ps -aq)')
        self._drone.vc.ssh_exec('docker rm $(docker ps -aq)')
        # remove all docker images
        self._drone.vc.ssh_exec('docker rmi $(docker images -q)')
        return self._set_state_based_on_success(True)
