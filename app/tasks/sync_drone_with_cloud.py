#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
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

import json
import os.path
import re

from ninox_common.drone_id import is_valid_drone_id
from ninox_common.drone_api_helper import get_companion_configuration, get_companion_version
from ninox_common.ninoxator_api_helper import ninoxator_postback, log_upload_required, upload_companion_log, add_flight

from app.configurations.config import DRONE_IP, DRONE_ASSESTS_DIR, COMPANION_LOGS_DIR, DRONE_CONFIGURATION_DIR
from app.tasks.task_interface import TaskInterface


class SyncDroneWithCloud(TaskInterface):
    def __init__(self, drone=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "Sync Drone with Cloud"
        self._with_halo = False

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("SyncDroneWithCloud go")
        drone_id = self.get_drone().cc.get_drone_id_from_drone_info()
        print(f"Drone ID from drone_info: {drone_id}")
        if not is_valid_drone_id(drone_id):
            self._errors.append(f"Invalid Drone ID from Drone Info: {drone_id} ")
            return self._set_state_based_on_success(False)

        network_id = get_companion_configuration()['COMMUNICATION_UNIT']['network_id']
        print(f"Network ID from Companion Configuration: {network_id}")
        companion_version = get_companion_version()
        print(f"Companion Version: {companion_version}")
        launch_count = self.get_drone().cc.get_launch_count()
        print(f"Launch Count: {launch_count}")
        if launch_count is None:
            self._errors.append('Failed to get Launch Count')
            return self._set_state_based_on_success(False)

        print('Going through logs')
        self.get_drone().empty_assets()
        for filename in self.get_drone().cc.cc_helper.list_files_in_directory(COMPANION_LOGS_DIR):
            print(f" filename: {filename}")
            local_file_full_path = f"{DRONE_ASSESTS_DIR}/{filename}"
            self.get_drone().cc.cc_helper.download_file(local_file_full_path, f"{COMPANION_LOGS_DIR}/{filename}")
            file_size = os.path.getsize(local_file_full_path)
            if file_size <= 0:
                print('  skipping: file_size 0')
                continue

            with open(local_file_full_path, 'r') as file:
                first_line = file.readline()
                m = re.search('log-uuid: (.+?)$', first_line)
                if not m:
                    print('  couldn\'t find uuid')
                    continue

                found = m.group(1)
                print(f"  log-uuid: {found}")

            _, file_extension = os.path.splitext(filename)
            print(f"  file_extension: {file_extension}")
            closed_file = file_extension != '.log'
            print(f"  params_for_log: { {'drone_id': drone_id, 'uuid': found, 'closed_file': closed_file} }")
            if not log_upload_required(drone_id, found, closed_file):
                print('  skipping: log_upload not required')
                continue

            print('  uploading')
            success = upload_companion_log(drone_id, found, closed_file, local_file_full_path)
            print(f"  upload success:{success}")

        print('Going through launches')
        file_name = 'launches_log_file.json'
        file_content = self.get_drone().cc.cc_helper.read_file(f"{DRONE_CONFIGURATION_DIR}/{file_name}")
        dic = json.loads(file_content)
        for launch in dic['launches']:
            print(' adding flight')
            success = add_flight(drone_id, launch.get('number'), launch['location']['lat'], launch['location']['long'],
                                 launch.get('date'), launch.get('session_id'))
            print(f" flight added: {success}")

        drone_params = {'network_id': network_id, 'cc_version': companion_version, 'launch_count': launch_count}
        print(f"Drone Params to Send: {drone_params}")
        success = ninoxator_postback(drone_params, drone_id=drone_id)
        return self._set_state_based_on_success(success)
