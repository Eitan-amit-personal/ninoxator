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

from enum import Enum
from typing import Union


class TaskStatusEnum(Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    ERROR = "ERROR"


class TaskStatus:
    __status: TaskStatusEnum
    __status_progress: int
    __step: Union[str, None]
    __step_progress: int

    def __init__(self, status: TaskStatusEnum, status_progress: int, step: Union[str, None], step_progress: int):
        if (status_progress < -1 or status_progress > 100) or (step_progress < -1 or step_progress > 100):
            raise BadInputException

        self.__status = status
        self.__status_progress = status_progress
        self.__step = step
        self.__step_progress = step_progress

    def set_task_status(self, status=None, status_progress=None, step=None, step_progress=None):
        if status is not None:
            self.__status = status
        if status_progress is not None:
            self.__status_progress = status_progress
        if step is not None:
            self.__step = step
        if step_progress is not None:
            self.__step_progress = step_progress

    def is_status_error(self):
        return self.__status == TaskStatusEnum.ERROR


class BadInputException(Exception):
    pass
