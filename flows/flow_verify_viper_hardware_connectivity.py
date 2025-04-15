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
from app.helpers.cli_helper import print_logo, print_instructions, print_error, print_success, error_text, success_text
from app.tasks.task_companion_computer_ping import CompanionComputerPingTask
from app.tasks.task_drone_ping import DronePingTask
from app.tasks.task_verify_ardupilot_device_exist import ArdupilotDeviceExistTask
from app.tasks.task_verify_attack_mcu_exist import AttackMcuExistTask
from app.tasks.task_verify_gimbal_mcu_exist import GimbalMcuExistTask
from app.tasks.task_verify_nanopi_version import NanopiVersionVerifyTask
from app.tasks.task_verify_nanopi_without_sd_card import NanopiWithoutSDCardTask
from app.tasks.task_vision_computer_ping import VisionComputerPingTask
from version import get_version


def viper_drone_verify_hardware_flow() -> bool:
    drone_connector = Drone(CONNECTION_STRING)

    with Halo(text="Waiting for drone to wakeup", spinner='bouncingBar') as spinner:
        status = task_runner.execute_task(DronePingTask, drone_connector)
        if status is False:
            spinner.fail(error_text("Can't connect to drone, check connections and retry"))
            return False
        else:
            spinner.succeed(success_text("Drone is connected and alive !"))

    task_list = [CompanionComputerPingTask(),
                 VisionComputerPingTask(),
                 GimbalMcuExistTask(),
                 AttackMcuExistTask(),
                 ArdupilotDeviceExistTask(),
                 NanopiWithoutSDCardTask(),
                 NanopiVersionVerifyTask()]

    all_successful = True
    for num, task in enumerate(task_list):
        print("")
        print(f"Step {num + 1} - {task.get_procedure_name()}")
        task.prerequisites()
        if task.is_status_error():
            print_error("Prerequisites failed!")
            all_successful = False
            continue
        with Halo(text=f'Executing {task.get_procedure_name()} ', spinner='dots') as spinner:
            step_success = task.go()
            text = f"{task.get_procedure_name()} success: {step_success}"
            if step_success:
                spinner.succeed(success_text(text))
            else:
                spinner.fail(error_text(text))
            all_successful = all_successful and step_success

    print('')
    if all_successful:
        print_success('HW connectivity verification passed ')
    else:
        print_error("HW connectivity verification failed !")

    return all_successful


def main():
    print_logo()
    print_instructions(f"Ninoxator version {get_version()}")
    print_instructions("")
    print_instructions('Connect Ethernet cable to communication connector')
    print_instructions('Turn Drone on')
    viper_drone_verify_hardware_flow()
    print_success('')
    print_success("You may disconnect the drone")
    input("Press Enter...")


if __name__ == '__main__':
    main()
