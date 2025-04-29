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

import ninox_common.drone_api_helper
from colors import color
from ninox_common.drone_id import is_valid_drone_id
from ninox_common.log import Loggable

from app.drone import Drone
from app.helpers.debug_helper import verbose_mode
from app.helpers.global_parameters_helper import get_drone_id, get_drone_id_from_user
from app.tasks.task_status import TaskStatus, TaskStatusEnum


class TaskInterface(Loggable):
    __status: TaskStatus
    _procedure_name: str
    _errors: list
    _drone: Drone
    _prerequisite: list

    def __init__(self, drone=None, drone_id=None, local_file=None, version=None, **kwargs):
        super().__init__()
        self.__status = TaskStatus(TaskStatusEnum.NOT_READY, -1, None, -1)
        self._errors = []
        self._drone = drone
        self._drone_id = drone_id
        self._prerequisite_pingable_ip: str = ''
        self._prerequisite_drone_id: bool = False
        self._prerequisite_flight_controller_firmware: bool = False

    def go(self) -> bool:
        self.logger.debug(f"{self._procedure_name} go")
        return self._go_internal()

    def _go_internal(self) -> bool:
        raise NotImplementedError

    def prerequisites(self) -> bool:
        result = self._execute_prerequisite_pingable_ip()
        if result:
            result = result and self._execute_prerequisite_drone_id()
            result = result and self._execute_prerequisite_flight_controller_firmware()
        if not result:
            self.set_task_status_error()
        return result

    def _execute_prerequisite_flight_controller_firmware(self):
        if self._prerequisite_flight_controller_firmware:
            raise NotImplementedError
        else:
            return True

    def _execute_prerequisite_drone_id(self) -> bool:
        if self._drone_id is not None:
            return True

        if self._prerequisite_drone_id and not is_valid_drone_id(get_drone_id()):
            self._drone_id = get_drone_id_from_user()
        return True

    def _execute_prerequisite_pingable_ip(self) -> bool:
        result = True
        if self._prerequisite_pingable_ip != '':
            result = ninox_common.drone_api_helper.is_pingable(self._prerequisite_pingable_ip, 1)
        return result

    def get_drone(self) -> Drone:
        return self._drone

    def get_procedure_name(self) -> str:
        return self._procedure_name

    def get_errors(self) -> list:
        return self._errors

    def get_task_status(self) -> TaskStatus:
        return self.__status

    def set_task_status(self, status=None, status_progress=None, step=None, step_progress=None):
        txt = f"set_status({status}, {status_progress}, {step}, {step_progress})"
        self.logger.info(txt)
        if step is not None and verbose_mode():
            print(color('>', fg='green'), step)
        self.__status.set_task_status(status, status_progress, step, step_progress)

    def set_task_status_ready(self):
        self.set_task_status(status=TaskStatusEnum.READY)

    def set_task_status_in_progress(self):
        self.set_task_status(status=TaskStatusEnum.IN_PROGRESS)

    def set_task_status_done(self):
        self.set_task_status(status=TaskStatusEnum.DONE, status_progress=100, step_progress=100)

    def set_task_status_error(self):
        self.set_task_status(status=TaskStatusEnum.ERROR, status_progress=-1, step_progress=-1)

    def is_status_error(self):
        return self.__status.is_status_error()

    def _set_state_based_on_success(self, success: bool):
        if success:
            self.set_task_status_done()
        else:
            self._errors.append(f"{self._procedure_name} failed ")
            self.set_task_status_error()

        return success

    def __loop_until_ip_reachable(self, timeout_sec=10, ip_address: str = '') -> bool:
        return ninox_common.drone_api_helper.loop_until_drone_reachable(max_time_for_pinging_seconds=timeout_sec)
