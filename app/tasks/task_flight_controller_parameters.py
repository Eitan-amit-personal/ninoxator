#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
# All rights reserved.
#
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import os
import shutil
import time

from ninox_common.configuration import DRONE_CONFIGURATION_DIR

from app.configurations.config import DRONE_IP
from app.drone_kit_wrapper import DRONE_ID_PARAM_NAME
from app.tasks.task_interface import TaskInterface

# CONSTS
MAX_WRITE_ATTEMPTS = 3
SLEEP_TIME_SEC = 15


class FlightControllerParametersUpdateTask(TaskInterface):
    ardupilot_ports = {'ArduPilot', 'MatekH743'}
    black_list_ports = {'SLCAN'}

    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone, drone_id=drone_id)
        self._drone_id = drone_id
        self._prerequisite_drone_id = True
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "Ardupilot Flight Controller Parameters"
        self.__parameters_file_full_path = local_file
        self.already_set = []
        self.updated = []
        self.error_keys = []
        self.write_loop_iterations_count = 0

        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.set_task_status(step='Connecting to flight controller')
        self.logger.debug('Connecting to flight controller')
        self.drone_kit_wrapper = self.get_drone().get_drone_kit_wrapper()
        self.drone_kit_wrapper.create_vehicle_connection()

        if self.drone_kit_wrapper.vehicle is None:
            self.logger.error('Could not connect to flight controller')
            return self._set_state_based_on_success(False)

        try:
            content = open(self.__parameters_file_full_path, 'r').read()
        except FileNotFoundError:
            self.logger.error('Could not open parameter file')
            return self._set_state_based_on_success(False)

        self.logger.info("Starting update write loop")
        self.write_loop_iterations_count = 0

        for i in range(1, MAX_WRITE_ATTEMPTS + 1):
            self.set_task_status(step="Setting Drone ID")
            self.__set_drone_id(int(self._drone_id))
            self.set_task_status(step=f"Starting write loop iteration {i}")
            self.logger.info(f"Starting write loop iteration {i}")
            self.write_loop_iterations_count = i
            self.__reset_aggregators()
            for line in content.splitlines():
                try:
                    param, val = line.split(',')
                    val = float(val)
                    self.__set_vehicle_parameter(param, val)
                except ValueError:
                    self.logger.error(f"line.split error {line}")
            time.sleep(0.1)
            if self.success_condition():
                self.logger.info("Breaking write loop because job is done")
                break

        # backup original parameters file onto nanopi
        params_file_dir = os.path.dirname(self.__parameters_file_full_path)
        common_params_file = os.path.join(params_file_dir, 'ardupilot.param')   # give it same name each time
        shutil.copy(self.__parameters_file_full_path, common_params_file)
        self.logger.info(f"Saving copy of param file - {common_params_file}")
        self.set_task_status(step=f"Uploading parameters backup file - {DRONE_CONFIGURATION_DIR}/ardupilot.param")
        self._drone.cc.upload_file(common_params_file, DRONE_CONFIGURATION_DIR)

        success = self._set_state_based_on_success(self.success_condition())
        self.drone_kit_wrapper.close()
        return success

    def success_condition(self):
        return len(self.error_keys) == 0 and len(self.drone_kit_wrapper.updated) == 0

    def __set_vehicle_parameter(self, parameter, value):
        if parameter == DRONE_ID_PARAM_NAME:
            return
        try:
            self.drone_kit_wrapper.set_vehicle_parameter(parameter, value)
            self.logger.info(f"Set parameter {parameter} {value}")
            if parameter in self.error_keys:
                self.error_keys.remove(parameter)
        except Exception as e:
            self.logger.error(f"Exception: parameter {parameter} {str(e)}")
            self.error_keys.append(parameter)

    def __set_drone_id(self, new_drone_id):
        try:
            self.drone_kit_wrapper.set_drone_id(new_drone_id)
        except Exception as e:
            self.logger.error(f"Exception: __set_drone_id {new_drone_id} {str(e)}")
            self.error_keys.append(DRONE_ID_PARAM_NAME)

    def __reset_aggregators(self):
        self.logger.info("__reset_aggregators")
        self.error_keys = []
        self.drone_kit_wrapper.reset_aggregators()
