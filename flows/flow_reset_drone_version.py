#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
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
from halo import Halo

from app import task_runner
from app.configurations.config import CONNECTION_STRING
from app.drone import Drone
from app.helpers.cli_helper import print_success, print_error, print_instructions, print_logo
from app.tasks.task_drone_ping import DronePingTask
from version import get_version


def flash_reset_drone_version_flow() -> bool:
    print_logo()

    print_instructions(f"Ninoxator version {get_version()}")
    print_instructions("")
    print_instructions('Turn Drone on')

    drone_connector = Drone(CONNECTION_STRING)

    with Halo(text="Waiting for drone to wakeup", spinner='bouncingBar'):
        status = task_runner.execute_task(DronePingTask, drone_connector)

    if status is False:
        print_error("Can't connect to drone , check connections and retry")
        input("Press Enter...")
        return False

    print_success('Drone is connected and alive !')

    status = drone_connector.cc.reset_meal()
    if status:
        print_success("Drone version was reset ")
    else:
        print_error("Drone version reset failed !")

    input("Press Enter...")
    return status


if __name__ == "__main__":
    flash_reset_drone_version_flow()
