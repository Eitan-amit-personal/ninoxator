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

import pathlib

from app.configurations.config import VISION_COMPUTER_IP_ADDRESS
from app.tasks.task_interface import TaskInterface

current_path = str(pathlib.Path(__file__).parent.resolve())
LOCAL_UTILITY_DIR = pathlib.Path(current_path + '/../utilities/services')


class VisionComputerFlaskPyinstallerUpdateTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = VISION_COMPUTER_IP_ADDRESS
        self._procedure_name = "VC Flask Pyinstaller Update"
        self._image_file = local_file
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("VisionComputerFlaskPyinstallerUpdateTask go")
        success = True
        success = success and self._drone.vc.update_drone_ui_flask_pyinstaller(self._image_file)
        success = success and self._drone.vc.update_drone_ui_flask_service(
            f"{LOCAL_UTILITY_DIR}/drone-ui-flask-jetson.service")
        return self._set_state_based_on_success(success)
