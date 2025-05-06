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


class ServiceControlTask(TaskInterface):
    def __init__(self, drone=None, drone_id=None, local_file=None, version=None, service="", start_service=False):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = DRONE_IP
        self._service_name = service
        self._start_service = start_service
        self._procedure_name = f"Telemetry Service Stop Task - {self._service_name}"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("ServiceControlTask - go")

        if self._start_service:
            self.set_task_status(step=f"Enabling service {self._service_name}")
            self._drone.cc.enable_service(self._service_name)
            self.set_task_status(step=f"Starting service {self._service_name}")
            self._drone.cc.start_service(self._service_name)

            service_running = self._drone.cc.is_service_running(self._service_name)
            success = service_running is True
        else:
            self.set_task_status(step=f"Stopping service {self._service_name}")
            self._drone.cc.stop_service(self._service_name)
            self.set_task_status(step=f"Disabling service {self._service_name}")
            self._drone.cc.disable_service(self._service_name)

            service_running = self._drone.cc.is_service_running(self._service_name)

            self.set_task_status(step="Rebooting NanoPi")
            self._drone.cc.reboot_computer()

            success = service_running is False

        return self._set_state_based_on_success(success)
