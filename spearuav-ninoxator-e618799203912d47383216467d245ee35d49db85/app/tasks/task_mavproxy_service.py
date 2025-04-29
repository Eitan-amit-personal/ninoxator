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
import pathlib

from ninox_common.cc_helper import MAVPROXY_SERVICE

from app.configurations.config import DRONE_IP
from app.tasks.task_interface import TaskInterface

current_path = str(pathlib.Path(__file__).parent.resolve())
LOCAL_UTILITY_DIR = pathlib.Path(current_path + '/../utilities/arm32/')


class MAVProxyServiceTask(TaskInterface):
    def __init__(self, drone=None, run_cmd=''):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = "MAVProxy Service Task"
        self._run_cmd = run_cmd
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("MAVProxy Service Task - go")

        self.set_task_status(step="Remove old mavproxy service")
        self._drone.cc.remove_service(MAVPROXY_SERVICE)
        self._drone.cc.reload_daemon()

        self.set_task_status(step="Upload and install wheel files")
        self._drone.cc.pip_install_global(f"{LOCAL_UTILITY_DIR}/pymavlink-2.4.40-py3-none-any.whl")
        self._drone.cc.pip_install_global(f"{LOCAL_UTILITY_DIR}/MAVProxy-1.8.67-py3-none-any.whl")

        self.set_task_status(step="Install service daemon")
        service_content = f'''
                [Unit]
                Description=Spearuav Drone Mavproxy Service
                After=network.target

                [Service]
                User=root
                WorkingDirectory=/root/.pyenv/
                ExecStart=/root/.pyenv/shims/mavproxy.py {self._run_cmd}
                Type=simple
                Restart=always
                RestartSec=4

                [Install]
                WantedBy=multi-user.target
                '''
        self._drone.cc.stop_service(MAVPROXY_SERVICE)
        self._drone.cc.install_service(MAVPROXY_SERVICE, service_content)

        succeeded = self._drone.cc.has_service(MAVPROXY_SERVICE)
        return self._set_state_based_on_success(succeeded)
