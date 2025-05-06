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
from ninox_common import monday_helper

from app import task_runner
from app.configurations.config import CONNECTION_STRING
from app.drone import Drone
from app.helpers.cli_helper import print_instructions, print_error, print_logo, print_success
from app.helpers.global_parameters_helper import get_drone_id_from_user
from app.tasks.task_drone_ping import DronePingTask
from app.tasks.task_set_drone_id_in_drone_info import SetDroneIdInDroneInfoTask
from version import get_version


def drone_set_drone_id_flow() -> bool:
    print_logo()

    print_instructions(f"Ninoxator version {get_version()}")
    print_instructions("")
    print_instructions('You are about to change the drone ID !')
    print_instructions('Make sure you know what you are doing')
    print_instructions("")
    drone_id = get_drone_id_from_user()

    if monday_helper.is_drone_exist(f'{drone_id}') is False:
        print_error(f"Drone id {drone_id} does not exist on Spearuav Monday system please check")
        input("Press Enter...")
        return False

    print_instructions('Turn Drone on')
    drone_connector = Drone(CONNECTION_STRING)

    with Halo(text="Waiting for drone to wakeup", spinner='bouncingBar'):
        status = task_runner.execute_task(DronePingTask, drone_connector)

    with Halo(text="Updating Drone ID", spinner='clock'):
        status = task_runner.execute_task(SetDroneIdInDroneInfoTask, drone_connector, drone_id)

    if status is False:
        print_error("Could not change drone ID!")
        input("Press Enter...")
    else:
        print_success(f'Drone ID changed successfully to {drone_id}')

    input("Press Enter...")
    return status


if __name__ == "__main__":
    drone_set_drone_id_flow()
