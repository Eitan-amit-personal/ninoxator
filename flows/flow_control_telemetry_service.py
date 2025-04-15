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

from halo import Halo
from ninox_common.cc_helper import TELEMETRY_SERVICE

from app import task_runner
from app.configurations.config import CONNECTION_STRING
from app.drone import Drone
from app.helpers.cli_helper import print_logo, print_instructions, print_error, print_success
from app.tasks.task_drone_ping import DronePingTask
from app.tasks.task_service_control import ServiceControlTask
from version import get_version


def control_telemetry_service_flow(start_service: bool):
    print_logo()

    print_instructions(f"Ninoxator version {get_version()}")
    print_instructions("")
    print_instructions('Connect Ethernet cable to communication connector')
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

    cmd = 'START' if start_service else 'STOP'
    with Halo(text=f"{cmd} TELEMETRY service", spinner='bouncingBar'):
        status = task_runner.execute_task(ServiceControlTask, drone_connector,
                                          service=TELEMETRY_SERVICE, start_service=start_service)
    if status is False:
        print_error(f"Cannot {cmd} service")
        return False
    else:
        print_success(f"Service {cmd} successfully")

    input("Press Enter...")
    return status
