#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
# All rights reserved.
#
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
from colorama import Fore, init

# init colorama
from ninox_common.drone_id import is_valid_drone_id

init()

SPEAR_LOGO = r"""
     ____
    / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
    \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
     ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
    |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
    """


def print_logo():
    print(SPEAR_LOGO)


def instruction_press_enter():
    input_in_yellow("Press Enter to continue...")


def instruction_insert_sd_and_restart():
    print_instructions("Please insert SD-card and restart drone.")
    instruction_press_enter()


def instruction_remove_sd_and_restart():
    print_instructions("Please turn off drone, then remove SD-card and then turn it back on.")
    instruction_press_enter()


def instruction_please_follow():
    print_instructions("Please follow these instructions:")


def input_in_yellow(input_str: str) -> str:
    return input(Fore.LIGHTYELLOW_EX + input_str)


def print_error(input_str: str):
    print_color(input_str, Fore.LIGHTRED_EX)


def print_success(input_str: str):
    print_color(input_str, Fore.LIGHTGREEN_EX)


def print_instructions(input_str: str):
    print_color(input_str, Fore.LIGHTYELLOW_EX)


def print_color(input_str: str, color_char):
    print(color_char + input_str)


def instructions_text(input_str: str) -> str:
    return colored_text(input_str, Fore.LIGHTYELLOW_EX)


def success_text(input_str: str) -> str:
    return colored_text(input_str, Fore.LIGHTGREEN_EX)


def error_text(input_str: str) -> str:
    return colored_text(input_str, Fore.LIGHTRED_EX)


def colored_text(input_str: str, color_char):
    return color_char + input_str


def drone_serial_from_user():
    serial_number: int = -1
    while serial_number == -1:
        serial_number_str = input_in_yellow("Please insert drone serial number: ")
        try:
            serial_number = int(serial_number_str)
            if not valid_drone_id(serial_number):
                print(" Drone ID must be: 0 < drone_id < 32767")
                print(" Try again")
                serial_number = -1
        except ValueError:
            serial_number = -1
            print(" Couldn't convert to integer.")

    print_color(f'Drone serial number is {serial_number}', Fore.LIGHTGREEN_EX)

    return serial_number


def valid_drone_id(drone_id_int: int):  # TODO delete when comfortable
    return is_valid_drone_id(drone_id_int)


def press_enter_to_continue():
    input()


def get_drone_type_and_hw_from_user():
    drone_types_str = [{'name': 'viper300 SpearEye', 'type': 'viper300', 'hw_version': '4.0'},
                       {'name': 'viper300 barrel', 'type': 'viper300', 'hw_version': '1.14.1'},
                       {'name': 'viper750', 'type': 'viper750', 'hw_version': '1.0.0'},
                       {'name': 'viper300 simulator', 'type': 'viper300', 'hw_version': '1.4.2'},
                       {'name': 'viper-s', 'type': 'viper-s', 'hw_version': '1.0.0'},
                       {'name': 'viper-i', 'type': 'viper-i', 'hw_version': '1.0.0'}
                       ]
    for index, drone_types in enumerate(drone_types_str):
        print_instructions(f"{index + 1}. {drone_types_str[index]['name']} ")

    drone_type_index = input_in_yellow('Please choose drone type:')
    hw_ver = drone_types_str[int(drone_type_index) - 1]
    return hw_ver


def get_drone_id_from_user():
    drone_id: int = -1
    drone_id_str: str = ''
    while drone_id_str == '':
        drone_id_str = input_in_yellow('Please enter Drone ID:')
        try:
            drone_id = int(drone_id_str)
            if not valid_drone_id(drone_id):
                drone_id_str = ''
        except ValueError:
            drone_id_str = ''

    return drone_id


def get_option_from_user(array_of_options):
    option = None
    while option is None:
        option = input_in_yellow("Enter option: ")
        try:
            option = int(option)
            if option not in array_of_options:
                option = None
            if option is None:
                print_instructions("Try again.")
        except ValueError:
            option = None
    return option


def get_comm_frequency_from_user(freq_min: int = 2100, freq_max: int = 2500) -> int:
    frequency: int = -1
    while frequency == -1:
        freq_str = input_in_yellow(f"Enter frequency ({freq_min} - {freq_max}): ")
        try:
            frequency = int(freq_str)
            if not (freq_min <= frequency <= freq_max):
                print(Fore.LIGHTRED_EX + " Frequency not in range")
                frequency = -1
        except ValueError:
            print(Fore.LIGHTRED_EX + " Cannot parse frequency")
            frequency = -1
    return frequency


def get_comm_mesh_from_user() -> int:
    mesh_id: int = -1
    while mesh_id == -1:
        mesh_id_str = input_in_yellow("Enter mesh ID (1 - 15): ")
        try:
            mesh_id = int(mesh_id_str)
            if not (1 <= mesh_id <= 15):
                print(Fore.LIGHTRED_EX + " ID not in range")
                mesh_id = -1
        except ValueError:
            print(Fore.LIGHTRED_EX + " Cannot parse number")
            mesh_id = -1
    return mesh_id
