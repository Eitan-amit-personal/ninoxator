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

from app.configurations.config import DRONE_IP
from app.tasks.task_interface import TaskInterface


class ServiceDeployTask(TaskInterface):
    def __init__(self, drone=None, service_name='', remove_service_name='', service_title='',
                 working_directory='', run_cmd='', restart_delay_sec=5, delay_sec=0, enabled=True):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._procedure_name = f"Service Deploy Task - {service_name}"
        self._service_name = service_name
        self._remove_service_name = remove_service_name
        self._service_title = service_title
        self._working_directory = working_directory
        self._run_cmd = run_cmd
        self._restart_delay_sec = restart_delay_sec
        self._delay_sec = delay_sec
        self._enabled = enabled
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("ServiceDeployTask Service Task - go")

        if self._remove_service_name != '':
            self.set_task_status(step="Removing old service")
            self._drone.cc.stop_service(self._remove_service_name)
            self._drone.cc.remove_service(self._remove_service_name)
            self._drone.cc.reload_daemon()

        self.set_task_status(step="Stopping current service")
        self._drone.cc.stop_service(self._service_name)
        self._drone.cc.remove_service(self._service_name)

        additional_service_cmd = ''
        if self._delay_sec > 0:
            self.set_task_status(step="Adding service delay")
            additional_service_cmd = f"ExecStartPre=/bin/sleep {self._delay_sec}"

        self.set_task_status(step="Installing service daemon")
        service_content = f'''
[Unit]
Description={self._service_title}
After=network.target

[Service]
Type=simple
Restart=always
RestartSec={self._restart_delay_sec}
User=root
WorkingDirectory={self._working_directory}
ExecStart={self._run_cmd}
{additional_service_cmd}

[Install]
WantedBy=multi-user.target
'''
        self._drone.cc.install_service(self._service_name, service_content)

        # usually services are installed enabled, however one can decide to disable them after install
        if not self._enabled:
            self.set_task_status(step="Disabling service")
            self._drone.cc.disable_service(self._service_name)
            self._drone.cc.reload_daemon()

        succeeded = self._drone.cc.has_service(self._service_name)
        return self._set_state_based_on_success(succeeded)
