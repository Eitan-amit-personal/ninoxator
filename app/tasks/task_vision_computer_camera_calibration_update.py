#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2024
# All rights reserved.
#
# __author__ = "Eden Ben Asulin"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import glob
from pathlib import Path

from app.tasks.task_interface import TaskInterface


class VisionComputerCameraCalibrationUpdateTask(TaskInterface):

    def __init__(self, drone=None, drone_id=None, local_file=None):
        super().__init__(drone=drone, drone_id=drone_id)
        # self._prerequisite_drone_id = True
        self._procedure_name = "Vision Computer Camera Calibration Update"
        self._local_file = local_file
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.set_task_status(step="Uploading camera calibration yaml files")
        status = self._check_and_update_vision_computer_calibration_files(self._local_file)
        return self._set_state_based_on_success(status)

    def _filter_yaml_files(self, files_list) -> list:
        return [f for f in files_list if f.endswith('.yaml')]

    def _check_and_update_vision_computer_calibration_files(self, local_files_list):
        local_files_list = glob.glob(local_files_list)

        # filter and leave only yaml files
        files_to_upload_list = self._filter_yaml_files(local_files_list)

        # filtered files that already exists
        files_to_upload_list = self._choose_files_to_upload(files_to_upload_list)

        # upload files
        result = self._drone.vc.upload_calibration_files(files_to_upload_list)

        return result

    def _choose_files_to_upload(self, file_list):
        calibration_files_list = file_list
        remote_file_list = self._filter_yaml_files(self._drone.vc.get_all_configuration_files_list())
        for local_calibration_file in calibration_files_list:
            local_file_name = Path(local_calibration_file).name
            for remote_file in remote_file_list:
                if remote_file == local_file_name:
                    yaml_content = self._drone.vc.read_remote_config_yaml_file(remote_file)
                    if yaml_content is not None:
                        calibration_status = yaml_content.get('calibration_status')
                        if calibration_status != 'default':
                            # don't replace file, remove from list
                            calibration_files_list.remove(local_calibration_file)
        return calibration_files_list
