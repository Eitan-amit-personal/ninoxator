#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
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
import pathlib
import os
import sys


from app.configurations.config import DRONE_IP
from app.tasks.task_interface import TaskInterface

def resource_path(relative_path):
    """Get absolute path to resource inside EXE or during development."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

LOCAL_UTILITY_DIR = resource_path('app/utilities/arm32')
UDEV_RULES_FOLDER = '/etc/udev/rules.d/'


class NanoPiRulesDeployTask(TaskInterface):
    def __init__(self, drone=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "NanoPi Rules Deploy"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        # update tty rule files - to support naming
        self.set_task_status(step=f"Uploading udev rules to {UDEV_RULES_FOLDER}")
        self._drone.cc.upload_file(
            local_path=os.path.join(LOCAL_UTILITY_DIR, '85-teensy_telem.rules'),target_path=UDEV_RULES_FOLDER)
        self._drone.cc.upload_file(
            local_path=os.path.join(LOCAL_UTILITY_DIR, '86-teensy_attack.rules'), target_path=UDEV_RULES_FOLDER)
        self._drone.cc.upload_file(
            local_path=os.path.join(LOCAL_UTILITY_DIR, '87-mro_aux.rules'), target_path=UDEV_RULES_FOLDER)
        self._drone.cc.upload_file(
            local_path=os.path.join(LOCAL_UTILITY_DIR, '88-mro.rules'), target_path=UDEV_RULES_FOLDER)
        return self._set_state_based_on_success(True)
