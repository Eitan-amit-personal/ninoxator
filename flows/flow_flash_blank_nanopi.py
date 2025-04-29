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
from app.helpers.cli_helper import print_instructions, print_error, print_logo, print_success
from app.tasks.task_cc_flash import CCFlashTask
from app.tasks.task_drone_ping import DronePingTask
from version import get_version


def flash_blank_nanopi_flow() -> bool:
    print_logo()

    print_instructions(f"Ninoxator version {get_version()}")
    print_instructions("")
    print_instructions('Connect Ethernet cable to communication connector')
    print_instructions("Insert SD-card to NANO PI SD card slot")
    print_instructions('Turn Drone on')

    drone_connector = Drone(CONNECTION_STRING)

    with Halo(text="Waiting for drone to wakeup", spinner='bouncingBar'):
        status = task_runner.execute_task(DronePingTask, drone_connector)

    if status is False:
        print_error("Can't connect to drone , check connections and retry")
        input("Press Enter...")
        return False

    print_success('Drone is connected and alive !')

    with Halo(text="Flashing NANO pi, it may take a while..", spinner='bouncingBar'):
        status = task_runner.execute_task(CCFlashTask, drone_connector)

    if status:
        print_success("Flashed successfully !")
        print_success("Remove SD card from NANO PI")
    else:
        print_error("NANO PI programming failed !")

    input("Press Enter...")
    return status


if __name__ == "__main__":
    flash_blank_nanopi_flow()
