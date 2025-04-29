#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2024
# All rights reserved.
#
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import logging
import os
import tarfile
import tempfile

from halo import Halo

from app import task_runner
from app.configurations.config import read_versions_directory, CONNECTION_STRING
from app.cookbook.cookbook import CookBook
from app.drone import Drone
from app.helpers.cli_helper import print_logo, print_instructions, print_error, print_success, get_drone_id_from_user, \
    get_option_from_user, get_comm_frequency_from_user, get_comm_mesh_from_user
from app.helpers.global_parameters_helper import set_drone_id, get_drone_id
from app.helpers.json_helper import is_valid_json
from app.utilities.tts.text_to_speech import speech_say
from flows.flow_cookbook_update import print_and_log, ingredient_parsed_to_task_list, create_ingredient_task_list, \
    print_ingredient_update_list
from app.tasks.task_comm_rf_enable import CommRfEnableTask
from app.tasks.task_drone_ping import DronePingTask
from app.tasks.task_get_drone_id_from_drone import GetDroneIdInDroneInfoTask
from app.tasks.task_set_drone_id_in_drone_info import SetDroneIdInDroneInfoTask
from app.tasks.task_set_drone_versions_in_drone_info import SetDroneVersionsInDroneInfoTask
from app.tasks.task_update_network_id import SetMicrohardNetworkIdTask
from flows.flow_verify_viper_hardware_connectivity import viper_drone_verify_hardware_flow
from version import get_version

logger = logging.getLogger("flow_cookbook_update")


def get_meal(meal_version: str, files: list) -> str:
    data = ""
    for file_name in files:
        if meal_version in os.path.basename(file_name):  # file_name is a full path which contains the version twice
            if file_name in files:
                with open(file_name) as file:
                    data = file.read()
                    break
    return data


def drone_local_cookbook_complete_update_flow() -> bool:
    drone_connector = Drone(CONNECTION_STRING)
    with Halo(text="Waiting for drone to wakeup", spinner='bouncingBar'):
        status = task_runner.execute_task(DronePingTask, drone_connector)
    if status is False:
        print_error("Can't connect to drone , check connections and retry")
        return False

    print_success('Drone is connected and alive !')

    status = task_runner.execute_task(GetDroneIdInDroneInfoTask, drone_connector, set_drone_id_func=set_drone_id)
    if status is False:
        print_error("Can't find drone ID in drone_info.")
        drone_id = get_drone_id_from_user()
        task_runner.execute_task(SetDroneIdInDroneInfoTask, drone_connector, drone_id)
    else:
        drone_id = get_drone_id()

    print_and_log(f"Drone ID is : {drone_id}")

    packed_releases_dir = read_versions_directory()
    print_and_log(f"Releases are at {packed_releases_dir}")
    available_versions = sorted(os.listdir(packed_releases_dir))
    # display versions
    print_instructions('Choose version')
    for index, version in enumerate(available_versions):
        print_instructions(f"{index + 1}. {version.replace('.tar.gz', '')}")

    option = get_option_from_user(list(range(1, len(available_versions) + 1)))
    index_picked = option - 1
    my_picked_release = available_versions[index_picked]

    print_and_log(f"Picked version {my_picked_release}")

    version_tar = tarfile.open(f"{packed_releases_dir}/{my_picked_release}", 'r')

    # extract all files to temporary folder
    temp_dir = tempfile.TemporaryDirectory()
    version_tar.extractall(path=temp_dir.name)

    speech_say("Starting software burn")
    print_and_log("Start software burn")

    # there is a subdirectory in the archive containing all the files that has the same name as the archive
    local_release_dir = f"{temp_dir.name}/{my_picked_release.rstrip('.tar.gz.json')}"
    release_files = [os.path.join(local_release_dir, f) for f in os.listdir(local_release_dir)]
    print(f"Extracting files to {local_release_dir}")
    meal = get_meal(my_picked_release.replace('.tar.gz', ''), release_files)
    next_meal = CookBook(meal)

    print_and_log(next_meal.recipe)
    print_and_log('Validate release files...')
    next_meal.recipe.fetch_files(local_release_dir)
    print_and_log('Done')

    selected_version = my_picked_release.replace('.tar.gz', '').split("-")
    drone_type = selected_version[0]
    hw_version = selected_version[1]

    drone = Drone(drone_id=drone_id, fc_connection_string=CONNECTION_STRING)
    current_meal = CookBook(drone.cc.get_current_drone_meal())

    print_and_log("")
    print_and_log(f'Drone current version is {current_meal.meal_version}')
    print_and_log(current_meal.recipe)

    ingredient_task_list = create_ingredient_task_list(current_meal, next_meal)

    is_microhard = False
    is_dtc = False
    for ingredient in ingredient_task_list:
        if 'microhard' in ingredient.name:
            is_microhard = True
            break
        if 'dtc' in ingredient_task_list:
            is_dtc = True
            break

    if not is_microhard and not is_dtc:
        print('Recipe has neither Microhard nor DTC ingredients, assuming no-comm configuration')

    print_ingredient_update_list(ingredient_task_list)

    task_list = []

    for ingredient_task in ingredient_task_list:
        received_task = ingredient_parsed_to_task_list(drone, ingredient_task, drone_id)
        if isinstance(received_task, list) and len(received_task) > 1:
            for task_part in received_task:
                task_list.append(task_part)
        else:
            task_list += received_task

    # before starting the burn tasks, turn off RF
    if is_microhard or is_dtc:
        with Halo(text='Disabling RF communication', spinner='dots'):
            step_success = task_runner.execute_task(CommRfEnableTask, drone_connector, is_dtc=is_dtc, enable=False)
        if step_success:
            print_success('Disabling RF communication succeeded')
        else:
            print_error('Disabling RF communication failed')

    all_successful = True
    status = drone.cc.reset_meal()
    for num, task in enumerate(task_list):
        print_and_log("")
        print_and_log(f"Step {num + 1} - {task.get_procedure_name()}")
        task.prerequisites()
        if task.is_status_error():
            print_error("Prerequisites failed!")
            all_successful = False
            break
        with Halo(text=f'Executing {task.get_procedure_name()} ', spinner='dots'):
            step_success = task.go()

        text = f"{task.get_procedure_name()} success: {step_success}"
        if step_success:
            print_success(text)
        else:
            print_error(text)
        all_successful = all_successful and step_success

    if all_successful:
        logger.info("All successful, setting drone info")
        # update drone-info
        status = task_runner.execute_task(SetDroneVersionsInDroneInfoTask,
                                          drone_connector,
                                          drone_id=drone_id,
                                          version=next_meal.meal_version,
                                          hw_version=hw_version,
                                          drone_type=drone_type)
        # update net id via API
        if is_microhard or is_dtc:
            logger.info("Setting communication params")
            frequency = 2479
            mesh_id = -1
            net_id = 2
            if is_dtc:
                print_instructions("DTC configuration:")
                frequency = get_comm_frequency_from_user()
                mesh_id = get_comm_mesh_from_user()
            status = status and task_runner.execute_task(
                SetMicrohardNetworkIdTask,
                drone_connector,
                drone_id=drone_id,
                is_dtc=is_dtc,
                net_id=net_id,
                frequency=frequency,
                mesh_id=mesh_id)

            # turn RF back on
            with Halo(text='Enabling RF communication', spinner='dots'):
                task_runner.execute_task(CommRfEnableTask, drone_connector, is_dtc=is_dtc, enable=True)
            if step_success:
                print_success('Enabling RF communication succeeded')
            else:
                print_error('Enabling RF communication failed')

        if status:
            print_success("Updated drone info and net id")
        else:
            print_error("Failed updating drone info or net id")

    all_successful = all_successful and status

    if all_successful:
        print_success('')
        print_success("Update recipe on drone")
        logger.info(f"updating meal file, meal json is valid - {is_valid_json(meal)}")
        updated = drone.cc.update_meal(meal)
        if not updated:
            print_error("Cannot update meal on drone!")
        print_success('')
        print_success(f"Drone {get_drone_id()} updated successfully to {next_meal.meal_version}")

        digits = [char for char in str(drone_id)]
        speech_say(f"Writing successful - drone {' '.join(digits)}")
    else:
        print_error("Drone update failed !")
        speech_say("ERROR, burn process did not succeed")

    temp_dir.cleanup()
    logger.info("Done cookbook update")

    # print_success("Shutting down the drone")
    # ninox_common.drone_api_helper.drone_shutdown()
    # print_success("You may disconnect the drone")


def main(check_hw=True):
    print_logo()
    print_instructions(f"Ninoxator version {get_version()}")
    print_instructions("")
    print_instructions('Connect Ethernet cables to Microhard connector')
    print_instructions('Turn Drone on')
    if check_hw:
        if viper_drone_verify_hardware_flow():
            drone_local_cookbook_complete_update_flow()
    else:
        drone_local_cookbook_complete_update_flow()
    input("Press Enter...")
