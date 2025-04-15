#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
# All rights reserved.
#
# __author__ = "Roie Geron"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import glob
import os

import unittest
from ninox_common.log import get_logger

from app import task_runner
from app.configurations.config import CONNECTION_STRING
from app.drone import Drone
from app.tasks.task_ap_lua_script import ArdupilotLuaScriptTask
from app.tasks.task_cc_flash import CCFlashTask
from app.tasks.task_cc_update import CCUpdateTask
from app.tasks.task_drone_mcu_attack_update import DroneMCUAttackUpdateTask
from app.tasks.task_drone_ping import DronePingTask
from app.tasks.task_drone_ui_flask_update import DroneUIFlaskUpdateTask
from app.tasks.task_drone_ui_flutter_update import DroneUIFlutterUpdateTask
from app.tasks.task_flight_controller_firmware_remote_update import (
    FlightControllerRemoteFirmwareUpdateTask,
)
from app.tasks.task_flight_controller_firmware_update import (
    FlightControllerFirmwareUpdateTask,
)
# from app.tasks.task_flight_controller_parameters import (
#     FlightControllerParametersUpdateTask,
# )
from app.tasks.task_get_drone_id_from_drone import GetDroneIdInDroneInfoTask
from app.tasks.task_set_drone_id_in_drone_info import SetDroneIdInDroneInfoTask
from app.tasks.task_set_drone_versions_in_drone_info import (
    SetDroneVersionsInDroneInfoTask,
)
from app.tasks.task_update_network_id import SetMicrohardNetworkIdTask
from app.tasks.task_verify_ardupilot_device_exist import ArdupilotDeviceExistTask
from app.tasks.task_verify_attack_mcu_exist import AttackMcuExistTask
from app.tasks.task_verify_gimbal_mcu_exist import GimbalMcuExistTask
from app.tasks.task_vision_computer_ping import VisionComputerPingTask
from app.tasks.task_vision_computer_update import VisionComputerUpdateTask
from app.tasks.task_vision_computer_update_pyinstaller import (
    VisionComputerUpdatePyinstallerTask,
)
from app.tasks.task_docker_deploy import DockerDeployTask

logger = get_logger(__name__)


@unittest.skipIf(True, "skipping tests that needs real drone connection")
class TasksTestCase(unittest.TestCase):
    def test_set_drone_id_task(self):
        test_drone_id = 8977
        drone_connector = Drone(CONNECTION_STRING)
        drone_id = task_runner.execute_task(
            SetDroneIdInDroneInfoTask, drone_connector, drone_id=test_drone_id
        )
        self.assertTrue(drone_id != "")

    def test_set_drone_versions_task(self):
        test_drone_hw_version = "1.7.2"
        test_drone_sw_version = "2.1.0"
        drone_type = "viper"
        drone_connector = Drone(CONNECTION_STRING)
        drone_id = task_runner.execute_task(
            SetDroneVersionsInDroneInfoTask,
            drone_connector,
            version=test_drone_sw_version,
            drone_type=drone_type,
            hw_version=test_drone_hw_version,
        )
        self.assertTrue(drone_id != "")

    def test_get_drone_id_task(self):
        drone_connector = Drone(CONNECTION_STRING)
        drone_id = task_runner.execute_task(GetDroneIdInDroneInfoTask, drone_connector)
        self.assertTrue(drone_id != "")

    def test_drone_ping_task(self):
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(DronePingTask, drone_connector)
        self.assertTrue(status)

    # def test_ardupilot_parameters_task(self):
    #     drone = Drone(drone_id=7777, fc_connection_string=CONNECTION_STRING)
    #     parameter_file = "data/VIPER.ZERO.4.3.2.param"
    #     status = task_runner.execute_task(
    #         FlightControllerParametersUpdateTask,
    #         drone_id=5218,
    #         drone=drone,
    #         local_file=parameter_file,
    #         version=None,
    #     )
    #     self.assertTrue(status)

    def test_cc_update_task(self):
        image_file = "data/ninox-companion-computer.tar.gz"
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(
            CCUpdateTask, drone_connector, drone_id=5218, local_file=image_file
        )
        self.assertTrue(status)

    def test_flask_update_task(self):
        image_file = "data/drone-ui-flask.tar.gz"
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(DroneUIFlaskUpdateTask, drone_connector, local_file=image_file)
        self.assertTrue(status)

    def test_flutter_update_task(self):
        image_file = "data/drone-ui-flutter.tar.gz"
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(
            DroneUIFlutterUpdateTask, drone_connector, local_file=image_file
        )
        self.assertTrue(status)

    def test_firmware_update_task(self):
        image_file = "data/arducopter.apj"
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(
            FlightControllerFirmwareUpdateTask, drone_connector, local_file=image_file
        )
        self.assertTrue(status)

    def test_set_microhard_network_id_task(self):
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(SetMicrohardNetworkIdTask, drone_connector, drone=None, drone_id=7777)
        self.assertTrue(status)

    def test_blank_nanopi_flash_task(self):
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(CCFlashTask, drone_connector)
        self.assertTrue(status)

    def test_update_mcu_attack(self):
        local_file = glob.glob(os.getcwd() + "/**/*.hex")[0]
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(
            DroneMCUAttackUpdateTask, drone_connector, local_file=local_file
        )
        self.assertTrue("Booting" in status)

    def test_remote_firmware_update_task(self):
        local_file = glob.glob(os.getcwd() + "/**/arducopter.apj")[0]
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(
            FlightControllerRemoteFirmwareUpdateTask, drone_connector, local_file=local_file
        )
        self.assertTrue(status)

    def test_vision_computer_pyinstaller_update_task(self):
        local_file = glob.glob(os.getcwd() + "/**/vision_computer")[0]
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(
            VisionComputerUpdatePyinstallerTask, drone_connector, local_file=local_file
        )
        self.assertTrue(status)

    def test_vision_computer_update_task(self):
        local_file = glob.glob(os.getcwd() + "/**/viper-payload-sw.tar.gz")[0]
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(
            VisionComputerUpdateTask, drone_connector, local_file=local_file
        )
        self.assertTrue(status)

    def test_ardupilot_device_exist_task_true(self):
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(ArdupilotDeviceExistTask, drone_connector)
        self.assertTrue(status)

    def test_gimbal_mcu_device_exist_task_true(self):
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(GimbalMcuExistTask, drone_connector)
        self.assertTrue(status)

    def test_attack_mcu_device_exist_task_true(self):
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(AttackMcuExistTask, drone_connector)
        self.assertTrue(status)

    def test_vision_computer_ping_true(self):
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(VisionComputerPingTask, drone_connector)
        self.assertTrue(status)

    def test_vision_computer_ping_false(self):
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(VisionComputerPingTask, drone_connector)
        self.assertFalse(status)

    def test_docker(self):
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(
            DockerDeployTask, drone_connector, local_file="ghcr.io/spearuav/vision-computer"
        )
        self.assertTrue(status)

    def test_ardupilot_script(self):
        script_file = "data/AP.lua"
        drone_connector = Drone(CONNECTION_STRING)
        status = task_runner.execute_task(
            ArdupilotLuaScriptTask, drone_connector, local_file=script_file, conn_string="/dev/ttyACM0"
        )
        self.assertTrue(status)
