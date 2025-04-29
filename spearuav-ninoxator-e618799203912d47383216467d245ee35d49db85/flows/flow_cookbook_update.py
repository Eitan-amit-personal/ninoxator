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
import logging

from colors import color
from halo import Halo
import json
from ninox_common import monday_helper, teams_helper
from ninox_common.git_wrapper import download_release_assets, get_latest_release_name
from packaging import version
from prettytable import PrettyTable
import tarfile
import tempfile
import os

from app import task_runner
from app.configurations.config import COOKING_ASSETS_DIR, CONNECTION_STRING
from app.cookbook.cookbook import CookBook
from app.cookbook.ingredient_transport import IngredientTransport
from app.drone import Drone
from app.helpers.cli_helper import print_logo, print_instructions, print_error, get_option_from_user, print_success, \
    get_drone_id_from_user, get_comm_frequency_from_user, get_comm_mesh_from_user, get_drone_type_and_hw_from_user
from app.helpers.debug_helper import verbose_mode
from app.helpers.global_parameters_helper import set_drone_id, get_drone_id
from app.helpers.json_helper import is_valid_json
from app.ingredients_echosystem.ingredient_factory import IngredientFactory
from app.tasks.task_comm_rf_enable import CommRfEnableTask
from app.tasks.task_drone_ping import DronePingTask
from app.tasks.task_get_drone_id_from_drone import GetDroneIdInDroneInfoTask
from app.tasks.task_set_drone_id_in_drone_info import SetDroneIdInDroneInfoTask
from app.tasks.task_set_drone_versions_in_drone_info import SetDroneVersionsInDroneInfoTask
from app.tasks.task_update_network_id import SetMicrohardNetworkIdTask
from app.utilities.tts.text_to_speech import speech_say
from flows.flow_verify_viper_hardware_connectivity import viper_drone_verify_hardware_flow
from version import get_version

logger = logging.getLogger("flow_cookbook_update")


COOKBOOK_REPO = 'spearuav/ninoxator-cookbook'
MAX_VERSIONS_TO_DISPLAY = 50


def print_and_log(s):
    print(s)
    logger.info(s)


def ingredient_parsed_to_task_list(my_drone, my_ingredient: IngredientTransport, drone_id):
    ingredient = IngredientFactory.name_to_ingredient(my_drone, my_ingredient, drone_id)

    if isinstance(ingredient, list):
        tasks = []
        for item in ingredient:
            tasks += item.prepare_tasks()
        return tasks
    elif ingredient is not None:
        return ingredient.prepare_tasks()
    else:
        return []


def get_version_from_user(drone_type: str, hw_version: str, cookbook_files: list, include_temporary: bool = False):
    hw_ver = version.parse(hw_version)
    relevant_releases = {}
    relevant_releases_names = []

    # get a list of all meals matching drone type and hardware version, return meal version and its tags
    for file_path in cookbook_files:
        file_name = os.path.basename(file_path)
        with open(file_path, 'r') as recipe_file:
            recipe = json.loads(recipe_file.read())
            meal_drone_type = recipe["meal_type"]
            meal_hw_version = recipe["meal_flavor"]
            meal_sw_version = recipe["meal_version"]
            description = recipe["meal_tags"]
            state = recipe["meal_state"]

            meal_version = version.parse(meal_hw_version)
            if drone_type == meal_drone_type and hw_ver.major == meal_version.major and hw_ver.minor == meal_version.minor:
                relevant_releases[meal_sw_version] = file_name
                if not state == "temporary" or (state == "temporary" and include_temporary):
                    relevant_releases_names.append(
                        {'version': meal_sw_version, 'description': description, 'state': state})

    # sort the list based on version reversed
    relevant_releases_names.sort(key=lambda x: x['version'], reverse=True)

    # display versions, with maximum number to display
    print_instructions('Choose version')
    for index, release in enumerate(relevant_releases_names[:MAX_VERSIONS_TO_DISPLAY]):
        release_marker = f" - {color('released', fg='black', bg='green')}" if release['state'] == "release" else ""
        print_instructions(f"{index + 1}. {release['version']}{release_marker}")

    # get user selection
    option = get_option_from_user(list(range(1, MAX_VERSIONS_TO_DISPLAY + 1)))
    index_picked = option - 1
    my_picked_release = relevant_releases[relevant_releases_names[index_picked]['version']]

    print_and_log(f"Picked version {relevant_releases_names[index_picked]['version']}")

    return my_picked_release


def get_compatible_meals(drone_type, drone_hw_version, release_dir):
    cookbook_files = download_release_assets(COOKBOOK_REPO, get_latest_release_name(COOKBOOK_REPO), release_dir,
                                             optimize_download=False)
    relevant_meals = []
    for meal in cookbook_files:
        try:
            meal_str = meal[:meal.rfind('.')]
            my_drone_type = meal_str.split('-')[0]  # assume meal in format drone-hw_version-software-version
            my_hw_version = meal_str.split('-')[1]
            my_software_version = meal_str.split('-')[2]
        except IndexError:
            continue

        if my_drone_type != drone_type:
            continue

        parsed_meal_hw_version = version.parse(my_hw_version)
        parsed_drone_hw_version = version.parse(drone_hw_version)
        if (parsed_meal_hw_version.minor == parsed_drone_hw_version.minor and
                parsed_meal_hw_version.major == parsed_drone_hw_version.major):
            relevant_meals.append(my_software_version)

    return relevant_meals


def get_meal(meal_version: str, cookbook_files: list) -> str:
    data = ''
    for file_name in cookbook_files:
        if meal_version in file_name:
            if file_name in cookbook_files:
                with open(file_name) as file:
                    data = file.read()
                    break
    return data


def create_ingredient_task_list(l_current_meal: CookBook, drone_next_meal: CookBook) -> list:
    #
    # my_ingredient_task_list = []
    # if l_current_meal.recipe is not None:  # we check what ingredients need to be updated
    #     for ingredient in drone_next_meal.recipe.get_ingredient_list():
    #         current_ingredient = l_current_meal.recipe.get_ingredient(ingredient.name)
    #         if current_ingredient is None or \
    #                 ingredient.version != current_ingredient.version or ingredient.force_update:
    #             my_ingredient_task_list.append(ingredient)
    # else:
    my_ingredient_task_list = drone_next_meal.recipe.get_ingredient_list()

    # Since it takes time for dronekit to recover from reboot after firmware upgrade
    # Moment make sure firmware parameters is last to give it a little time to recover

    index = next((ix for ix, item in enumerate(my_ingredient_task_list) if item.name == 'ardupilot-parameters'), -1)
    if index != -1:
        my_ingredient_task_list.append(my_ingredient_task_list.pop(index))

    return my_ingredient_task_list


def print_ingredient_update_list(ing_list: list):
    print_success('The following will be updated')
    x = PrettyTable()
    x.field_names = ["name", "version"]
    for ingredient in ing_list:
        x.add_row([ingredient.name, ingredient.version])
    x.align = "l"
    print_success(f'{x}')


def drone_cookbook_complete_update_flow() -> bool:
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

    # master switch to bypass monday
    use_monday = True

    if use_monday:
        # to speed up monday queries, fetch all boards here, and go into the result dictionary
        with Halo(text='Fetching drones data from Monday', spinner='dots'):
            drones_hw_info = monday_helper.get_drones_hw_from_boards_data()

        drone_id_str = f'{drone_id}'
        if drone_id_str not in drones_hw_info:
            print_error(f"Drone id {drone_id_str} does not exist on Spearuav Monday system please check")
            input("Press Enter...")
            return False

        with Halo(text='Getting drone type and HW version', spinner='dots'):
            drone_type = drones_hw_info[drone_id_str]["type"].lower().replace(' ', '')
            hw_version = drones_hw_info[drone_id_str]["hw_version"].lower()
    else:
        drones_hw_info = get_drone_type_and_hw_from_user()
        drone_type = drones_hw_info["type"].lower().replace(' ', '')
        hw_version = drones_hw_info["hw_version"].lower()

    if '(' in drone_type:
        drone_type = drone_type.split("(")[0].strip()
    print_and_log(f"Drone type is {drone_type}, hardware version {hw_version}")

    # from the latest release, download the cookbooks tar file which include all jsons
    releases_dir = f"{COOKING_ASSETS_DIR}/ninoxator-cookbook"
    latest_release = get_latest_release_name(COOKBOOK_REPO)
    cookbook_tar_name = download_release_assets(COOKBOOK_REPO, latest_release, releases_dir,
                                                asset_name='cookbooks.tar.gz', optimize_download=False)[0]
    cookbook_tar = tarfile.open(f'{releases_dir}/{cookbook_tar_name}', 'r')

    # extract all jsons to temporary folder
    temp_dir = tempfile.TemporaryDirectory()

    cookbook_tar.extractall(path=temp_dir.name)
    entries = os.listdir(temp_dir.name)
    cookbook_files = [os.path.join(temp_dir.name, entry) for entry in entries]

    picked_release = get_version_from_user(drone_type, hw_version, cookbook_files)
    print_and_log(f"Picked version {picked_release}")

    speech_say("Starting software burn")

    local_release_dir = f"{releases_dir}/{picked_release}"
    if not os.path.exists(local_release_dir):
        os.mkdir(local_release_dir)

    meal = get_meal(picked_release, cookbook_files)
    next_meal = CookBook(meal)

    print_and_log(next_meal.recipe)
    print_and_log('Download release files')
    next_meal.recipe.fetch_files(local_release_dir)
    print_and_log('Done')

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
        with Halo(text=f'Executing {task.get_procedure_name()} ', spinner='dots') as spinner:
            if verbose_mode():
                spinner.stop()  # spinner interferes with the stdout prints of verbose mode
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
        else:
            logger.info("Meal updated successfully")
        print_success('')
        print_success(f"Drone {get_drone_id()} updated successfully to {next_meal.meal_version}")
        if use_monday:
            print_success("Updating Spearuav Monday Dashboard")
            monday_helper.update_drone_version(str(drone_id), next_meal.meal_version)
        teams_helper.send_via_notifier(f"Drone {drone_id} updated to version {next_meal.meal_version}")

        digits = [char for char in str(drone_id)]
        speech_say(f"Writing successful - drone {' '.join(digits)}")
    else:
        print_error("Drone update failed !")
        speech_say("ERROR, burn process did not succeed")

    cookbook_tar.close()
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
            drone_cookbook_complete_update_flow()
    else:
        drone_cookbook_complete_update_flow()
    input("Press Enter...")
