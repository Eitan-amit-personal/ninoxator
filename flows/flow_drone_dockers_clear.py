#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
from halo import Halo

from app import task_runner
from app.configurations.config import CONNECTION_STRING
from app.drone import Drone
from app.helpers.cli_helper import print_logo, print_instructions, print_error, print_success
from app.tasks.task_drone_ping import DronePingTask
from app.tasks.task_vision_computer_docker_clear import VisionComputerDockerClearTask
from version import get_version


def drone_dockers_clear():
    print_logo()

    print_instructions(f"Ninoxator version {get_version()}")
    print_instructions("")
    print_instructions('Connect Ethernet cable to communication connector')
    print_instructions('Connect Ethernet cable to Vision Computer')
    print_instructions('Turn Drone on')
    print_instructions("")

    drone_connector = Drone(CONNECTION_STRING)

    with Halo(text="Waiting for drone to wakeup", spinner='bouncingBar'):
        status = task_runner.execute_task(DronePingTask, drone_connector)

    if status is False:
        print_error("Can't connect to drone , check connections and retry")
        return False

    print_success('Drone is connected and alive !')

    status = True
    if input("Press D to remove all dockers on drone:") == "D":
        print_instructions("!!!!! Removing dockers from drone !!!!!")
        status = task_runner.execute_task(VisionComputerDockerClearTask, drone_connector)
        if status is False:
            print_error("Error while clearing dockers on drone!")

    input("Press Enter...")
    return status
