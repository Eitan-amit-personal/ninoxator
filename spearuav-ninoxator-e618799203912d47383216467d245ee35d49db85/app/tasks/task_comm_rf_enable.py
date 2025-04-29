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

from app.configurations.config import DRONE_IP, COMMUNICATION_DEVICE_IP
from app.tasks.task_interface import TaskInterface

from ninox_python_infra_lib.communication_units.microhard import Microhard
from ninox_python_infra_lib.communication_units.dtc import Dtc


class CommRfEnableTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None, is_dtc=False, enable=False):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "Enable/Disable RF comm on drone"
        self.set_task_status_ready()
        self._is_dtc = is_dtc
        self._rf_enable = enable

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("CommRfEnableTask go")

        # sense if this drone has DTC communication device or MH, and enable/disable comm
        if self._is_dtc:
            dtc = Dtc(COMMUNICATION_DEVICE_IP, 'admin', 'Spear4010')
            if self._rf_enable:
                status = dtc.set_radio_on()
            else:
                status = dtc.set_radio_off()
        else:
            mh = Microhard(COMMUNICATION_DEVICE_IP, 'admin', 'Spear4010')
            if self._rf_enable:
                status = mh.set_radio_on()
            else:
                status = mh.set_radio_off()
            mh.enable_config_change()

        return self._set_state_based_on_success(status)
