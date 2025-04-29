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
import pathlib

from app.configurations.config import VISION_COMPUTER_IP_ADDRESS
from app.tasks.task_interface import TaskInterface

current_path = str(pathlib.Path(__file__).parent.resolve())
LOCAL_UTILITY_DIR = pathlib.Path(current_path + '/../utilities/arm64/')
UDEV_RULES_FOLDER = '/etc/udev/rules.d/'


class JetsonRulesDeployTask(TaskInterface):
    def __init__(self, drone=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = VISION_COMPUTER_IP_ADDRESS
        self._procedure_name = "Jetson Rules Deploy"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        # update tty rule files - to support naming
        self.set_task_status(step=f"Uploading udev rules to {UDEV_RULES_FOLDER}")
        self._drone.vc.upload_file(
            local_path=f"{LOCAL_UTILITY_DIR}/85-gimbal_aux.rules", target_path=UDEV_RULES_FOLDER)
        self._drone.vc.upload_file(
            local_path=f"{LOCAL_UTILITY_DIR}/86-gimbal_cli.rules", target_path=UDEV_RULES_FOLDER)
        self._drone.vc.upload_file(
            local_path=f"{LOCAL_UTILITY_DIR}/87-gimbal_micro_ros.rules", target_path=UDEV_RULES_FOLDER)
        return self._set_state_based_on_success(True)
