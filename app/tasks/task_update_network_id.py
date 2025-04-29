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

from app.configurations.config import DRONE_IP
from app.tasks.task_interface import TaskInterface


class SetMicrohardNetworkIdTask(TaskInterface):
    def __init__(self, drone_id, drone=None, local_file=None, version=None, is_dtc=False,
                 net_id=1234, frequency=2479, mesh_id=-1):
        super().__init__(drone=drone, drone_id=drone_id, local_file=local_file, version=version)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "Set Microhard Network ID"
        self._is_dtc = is_dtc
        self._network_id = net_id
        self._frequency = frequency
        self._mesh_id = mesh_id
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("SetMicrohardNetworkIdTask go")
        new_network_id = self._network_id if self._is_dtc else f'ninox_{self._drone_id}'
        success = self.get_drone().cc.set_communication_info(
            'dtc' if self._is_dtc else 'microhard', self._frequency, new_network_id, self._mesh_id)
        return self._set_state_based_on_success(success)
