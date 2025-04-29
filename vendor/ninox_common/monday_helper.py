#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2022
# All rights reserved.
#
# __author__ = "Roie Geron"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################


import requests
from monday import MondayClient

from ninox_common.vault_service import get_secret

ninox_40_board_id = 3434684774
sw_version_board_id = 2712296651
viper_300_board_id = 3434649016
viper_750_board_id = 5718128359
halilan_board_id = 3894254678

DRONE_BOARDS = [ninox_40_board_id,
                viper_300_board_id,
                viper_750_board_id,
                halilan_board_id]

DRONE_TYPES = ['ninox40', 'viper300', 'viper750', 'halilan']
monday_apikey = get_secret('monday-apikey')
headers = {"Authorization": monday_apikey['password'], 'API-Version': '2024-04'}
my_monday = MondayClient(monday_apikey['password'])
apiUrl = "https://api.monday.com/v2"


def get_all_boards_data():
    query = "{{boards(ids: [{} , {}, {}, {}]) {{ name id items_page(limit: 500) " \
            "{{ items {{ name column_values {{ ... on BoardRelationValue {{ display_value }} column {{ id title }} id text type }} }} }} }} }}"
    query = query.format(ninox_40_board_id, viper_300_board_id, viper_750_board_id, halilan_board_id)
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)  # make request
    return r.json()


def get_drones_hw_from_boards_data() -> dict:
    boards_json = get_all_boards_data()
    drones_dict = {}
    for board in boards_json["data"]["boards"]:
        for item in board["items_page"]["items"]:
            drone_id = item["name"]
            for column in item["column_values"]:
                if column["column"]["title"] == "Hardware Version":
                    drone_hw = column["display_value"]
                    drones_dict[drone_id] = {"hw_version": drone_hw, "type": board["name"]}
                    break

    return drones_dict


def get_drone_type(drone_id: str):
    drone_type = ''
    for drone_board in DRONE_BOARDS:
        if is_item_exist(drone_board, drone_id):
            drone_type = DRONE_TYPES[DRONE_BOARDS.index(drone_board)]

    return drone_type


def get_boards():
    boards = my_monday.boards.fetch_boards()
    return boards


def get_workspaces():
    workspaces = my_monday.workspaces.get_workspaces()
    return workspaces


def get_col_id_by_title(board: int, title: str):
    columns = my_monday.boards.fetch_columns_by_board_id(board)['data']['boards'][0]['columns']
    for column in columns:
        if column['title'] == title:
            return column['id']
    return None


def launches_col_id():
    return get_col_id_by_title(sw_version_board_id, 'Launches')


def flight_time_col_id():
    return get_col_id_by_title(sw_version_board_id, 'Flight time')


def software_version_col_id(board):
    return get_col_id_by_title(board, 'Software Version')


def hardware_version_col_id(board):
    return get_col_id_by_title(board, 'Hardware Version')


def drone_id_to_id(drone_id: str):
    board_id = get_drone_board_id(drone_id)
    if board_id is not None:
        ninox_items = my_monday.boards.fetch_items_by_board_id(board_id, limit=500)
        try:
            if ninox_items is not None:
                drones = ninox_items['data']['boards'][0]['items_page']['items']
                for drone in drones:
                    if drone['name'] == drone_id:
                        return drone['id']
        except KeyError:
            return None

    return None


def software_version_id_to_id(software_version: str):
    software_versions_items = my_monday.boards.fetch_items_by_board_id(sw_version_board_id, limit=500)
    items = software_versions_items['data']['boards'][0]['items_page']['items']
    for item in items:
        if item['name'] == software_version:
            return item['id']
    return None


def is_item_exist(board: int, item: str) -> bool:
    monday_items = my_monday.boards.fetch_items_by_board_id(board, limit=500)
    items = monday_items['data']['boards'][0]['items_page']['items']
    for my_item in items:
        if my_item["name"] == item:
            return True

    return False


def is_software_version_exist(version_str: str):
    return is_item_exist(sw_version_board_id, version_str)


def is_drone_exist(drone_id: str):
    for drone_board in DRONE_BOARDS:
        if is_item_exist(drone_board, drone_id):
            return True
    return False


def get_drone_board_id(drone_id: str):
    for drone_board in DRONE_BOARDS:
        if is_item_exist(drone_board, drone_id):
            return drone_board
    return None


def get_drone_hw_version(drone_id: str):
    drones_hw = get_drones_hw_from_boards_data()
    return drones_hw[drone_id] if drone_id in drones_hw else None


def update_drone_version(drone_id: str, version: str):
    response = None
    board = get_drone_board_id(drone_id)
    if board is not None:
        monday_drone_id = drone_id_to_id(drone_id)
        response = my_monday.items.change_item_value(board, monday_drone_id, software_version_col_id(board),
                                                     version)
    return response


def update_flight_time(software_version: str, flight_time: int):
    response = None
    if is_software_version_exist(software_version):
        monday_flight_time_id = software_version_id_to_id(software_version)
        response = my_monday.items.change_item_value(sw_version_board_id, monday_flight_time_id,
                                                     flight_time_col_id(),
                                                     flight_time)
    return response


def update_version_launch_counter(software_version: str, launches: int):
    response = None
    if is_software_version_exist(software_version):
        monday_flight_time_id = software_version_id_to_id(software_version)
        response = my_monday.items.change_item_value(sw_version_board_id, monday_flight_time_id,
                                                     launches_col_id(),
                                                     launches)
    return response


def get_drones_list() -> dict:
    drones_list = {}
    for board in DRONE_BOARDS:
        monday_items = my_monday.boards.fetch_items_by_board_id(board, limit=500)
        board = monday_items['data']['boards'][0]
        drone_type = board['name']
        drones = board['items_page']['items']
        for drone in drones:
            drone_id = drone['name']
            if drone_id not in drones_list:     # do not overwrite if already exists
                drones_list[drone_id] = drone_type

    return drones_list
