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

from ninox_common.drone_id import is_valid_drone_id

from app.drone_kit_wrapper import DRONE_ID_PARAM_NAME
from app.tasks.task_flight_controller_firmware_update import FlightControllerFirmwareUpdateTask
from app.helpers.common_helper import get_from_ninox_drone_configuration_files
from app.helpers.global_parameters_helper import get_drone_id
from app.tasks.task_interface import TaskInterface


class ValidateFcParameters(TaskInterface):
    def __init__(self, parameters_filename='Fatboy TNE - LAB.param', drone=None):
        super().__init__(drone=drone)
        self._prerequisite_flight_controller_firmware = True
        self.parameters_filename = parameters_filename
        self._procedure_name = "Validate FC Parameters"
        self.flight_controller_firmware = FlightControllerFirmwareUpdateTask()
        self.drone_kit_wrapper = None
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.logger.debug("ValidateFcParameters")
        successful = False
        self.drone_kit_wrapper = self.get_drone().get_drone_kit_wrapper()
        content = get_from_ninox_drone_configuration_files(self.parameters_filename)
        for line in content.splitlines():
            param, val = line.split(',')
            if param == DRONE_ID_PARAM_NAME:
                if is_valid_drone_id(get_drone_id()):
                    val = get_drone_id()
                else:
                    continue

            val = float(val)
            successful = self.drone_kit_wrapper.is_parameter_equal(param, val)
            self.logger.debug(f"{param} is equal: {successful}")
            if not successful:
                self.logger.debug(f"value from file: {val}")
                self.logger.debug(f"value from drone: {self.drone_kit_wrapper.get_vehicle_parameter(param)}")
                break

        return self._set_state_based_on_success(successful)
