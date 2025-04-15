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

from halo import Halo

from app import task_runner
from app.configurations.config import CONNECTION_STRING
from app.drone import Drone
from app.helpers.cli_helper import print_logo, print_instructions, print_error, print_success
from app.tasks.task_drone_mcu_attack_update import DroneMCUAttackUpdateTask
from app.tasks.task_drone_mcu_gimbal_update import DroneMCUGimbalUpdateTask
from app.tasks.task_drone_ping import DronePingTask
from app.tasks.task_vision_computer_ping import VisionComputerPingTask
from version import get_version

current_path = str(pathlib.Path(__file__).parent.resolve())
LOCAL_UTILITY_DIR = pathlib.Path(current_path + '/../app/utilities/')


def dual_teensy_reset():
    print_logo()

    print_instructions(f"Ninoxator version {get_version()}")
    print_instructions("")
    print_instructions('Connect Ethernet cable to communication connector')
    print_instructions('Connect Ethernet cable to Vision Computer')
    print_instructions('Turn Drone on')
    print_instructions("")

    drone_connector = Drone(CONNECTION_STRING)

    # NanoPi - attack mcu
    with Halo(text="Waiting NanoPi to wakeup", spinner='bouncingBar'):
        status = task_runner.execute_task(DronePingTask, drone_connector)
    if status is False:
        print_error("Can't connect to NanoPi, check connections and retry")
        return False
    else:
        print_success("NanoPi connected")

    with Halo(text="Connecting AMCU", spinner='bouncingBar'):
        status = task_runner.execute_task(
            DroneMCUAttackUpdateTask, drone_connector, local_file=f"{LOCAL_UTILITY_DIR}/teensy_triple_serial_blank.hex")
    if status is False:
        print_error("Error resetting AMCU")
        return False
    else:
        print_success("AMCU reset successfully")

    # Jetson - gimbal mcu
    with Halo(text="Waiting Jetson to wakeup", spinner='bouncingBar'):
        status = task_runner.execute_task(VisionComputerPingTask, drone_connector)
        if status is False:
            print_error("Can't connect to Jetson, check connections and retry")
            return False

    with Halo(text="Connecting GMCU", spinner='bouncingBar'):
        status = task_runner.execute_task(
            DroneMCUGimbalUpdateTask, drone_connector, local_file=f"{LOCAL_UTILITY_DIR}/teensy_triple_serial_blank.hex")
    if status is False:
        print_error("Error resetting GMCU")
        return False
    else:
        print_success("GMCU reset successfully")

    input("Press Enter...")
    return status
