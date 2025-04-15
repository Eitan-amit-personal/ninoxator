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
from ninox_common.cc_helper import CCHelper
from ninox_common.drone_id import is_valid_drone_id
from ninox_common.vision_computer_helper import VisionComputerHelper

from app.drone_kit_wrapper import DroneKitWrapper
from app.helpers.global_parameters_helper import get_drone_id, set_drone_id


class Drone:
    cc: CCHelper
    vc = VisionComputerHelper
    __drone_kit_wrapper: DroneKitWrapper

    def __init__(self, drone_id=None, fc_connection_string=None):
        self.fc_connection_string = None
        if drone_id is not None:
            set_drone_id(drone_id)
        if fc_connection_string is not None:
            self.fc_connection_string = fc_connection_string
        self.cc = CCHelper()
        self.vc = VisionComputerHelper()
        self.__drone_kit_wrapper = None
        self.__file_names_in_configuration = None

    def get_drone_kit_wrapper(self):
        if self.__drone_kit_wrapper == None:
            self.__connect_dkw()
        return self.__drone_kit_wrapper

    def set_drone_id_in_fc(self):
        if self.__drone_kit_wrapper == None:
            self.__connect_dkw()
        if not is_valid_drone_id(get_drone_id()):
            raise DroneIDNotSet
        self.__drone_kit_wrapper.set_drone_id(get_drone_id())

    def __connect_dkw(self):
        if self.__drone_kit_wrapper is not None and self.__drone_kit_wrapper.vehicle is not None:
            return
        else:
            self.__drone_kit_wrapper = None

        if self.fc_connection_string is None:
            raise FlightControllerConnectionStringEmpty

        self.__drone_kit_wrapper = DroneKitWrapper(self.fc_connection_string)


class DroneIDNotSet(Exception):
    """Drone ID is None"""
    pass


class FlightControllerConnectionStringEmpty(Exception):
    """Maybe _prerequisite_flight_controller_firmware should be set to True?"""
    pass
