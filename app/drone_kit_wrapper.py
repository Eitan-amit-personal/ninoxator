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

from time import sleep

import dronekit
import dronekit_sitl
from ninox_common.log import Loggable
import os
import sys

DRONE_ID_PARAM_NAME = "BRD_SERIAL_NUM"


class DroneKitWrapper(Loggable):
    def __init__(self, connection_string):
        super().__init__()
        self.already_set = []
        self.updated = []
        self.connection_string = connection_string
        self.vehicle: dronekit.Vehicle = None

    def create_vehicle_connection(self):

        print("[DEBUG] create_vehicle_connection() called")
        print(f"[DEBUG] CONNECTION STRING: {self.connection_string}")
        print(f"[DEBUG] RUNNING FROM: {getattr(sys, '_MEIPASS', os.getcwd())}")

        if self.vehicle is not None:
            print("[DEBUG] Vehicle already exists, returning existing instance")
            return self.vehicle

        if self.connection_string == 'sitl':
            print("[DEBUG] Using SITL mode")
            sitl = dronekit_sitl.start_default()
            self.connection_string = sitl.connection_string()

        my_vehicle = None
        while my_vehicle is None:
            try:
                print(f"[DEBUG] Trying to connect to {self.connection_string}")
                self.logger.info(f'Trying to connect to {self.connection_string}')

                import socket
                try:
                    print(f"DEBUG - Trying to connect to {self.connection_string}")
                    host, port = self.connection_string.split(':')
                    print(f"DEBUG - Can connect to {host}:{port}? ", end='')
                    with socket.create_connection((host, int(port)), timeout=5):
                        print("YES")
                except Exception as e:
                    print(f"NO - {e}")

                my_vehicle = dronekit.connect(self.connection_string, wait_ready=True, timeout=30, heartbeat_timeout=5)
                print(f"[DEBUG] Connected successfully to {self.connection_string}")
                self.logger.info(f"Connected to {self.connection_string}")
                self.vehicle = my_vehicle
            except dronekit.APIException as e:
                print(f"[ERROR] DroneKit APIException: {e}")
                self.logger.error(f'Could not connect to vehicle {e}')
                if my_vehicle is not None:
                    my_vehicle.close()
                my_vehicle = None
            except Exception as e:
                print(f"[ERROR] General exception: {str(e)}")
                self.logger.error(f"Exception - {str(e)}")
                if my_vehicle is not None:
                    my_vehicle.close()
                my_vehicle = None

        return my_vehicle

    def get_vehicle_parameter(self, parameter_name):
        return self.vehicle.parameters[parameter_name]

    def set_vehicle_parameter(self, parameter_name, value):
        if self.is_parameter_equal(parameter_name, value):
            self.logger.debug("value already set.")
            self.already_set.append(parameter_name)
        else:
            self.vehicle.parameters[parameter_name] = value
            self.updated.append(parameter_name)
            sleep(0.01)

    def is_parameter_equal(self, parameter_name, value):
        answer = False
        try:
            current_value = self.get_vehicle_parameter(parameter_name)
            answer = abs(round(current_value, 7) - value) <= 0.000001
        except KeyError:
            self.logger.info(f"Key Error {parameter_name}")
        return answer

    def get_version(self):
        return self.vehicle.version

    def get_status(self):
        return self.vehicle.system_status

    def close(self):
        if self.vehicle is not None:
            return self.vehicle.close()

    def reset_aggregators(self):
        self.already_set = []
        self.updated = []

    def get_drone_id(self):
        return self.get_vehicle_parameter(DRONE_ID_PARAM_NAME)

    def set_drone_id(self, new_drone_id):
        self.set_vehicle_parameter(DRONE_ID_PARAM_NAME, new_drone_id)
