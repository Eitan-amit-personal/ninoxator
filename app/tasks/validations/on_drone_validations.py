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

from app.tasks.task_interface import TaskInterface


class OnDroneValidations(TaskInterface):
    def __init__(self, drone=None):
        super().__init__(drone=drone)
        self._procedure_name = "On Drone Validations"
        self.validation_script_files = ["validate_cc_fc"]
        self.directory_name = "validations"
        self.set_task_status_ready()

    def _go_internal(self) -> bool:
        self.logger.debug("OnDroneValidations _go_internal")
        successful = True
        self.set_task_status_in_progress()
        self.get_drone().cc.cc_helper.ssh_exec_command_without_stdout(f"mkdir ~/{self.directory_name}")

        self.logger.debug("uploading validation files")
        for validation_file in self.validation_script_files:
            self.get_drone().cc.cc_helper.upload_file(f"validation_scripts/{validation_file}.py",
                                                      f"{self.directory_name}/{validation_file}.py")
        self.logger.debug("upload validation files done")

        self.logger.debug("running validations")
        for validation_file in self.validation_script_files:
            chan = self.get_drone().cc.cc_helper.open_session()
            chan.exec_command(f"python3 ~/{self.directory_name}/{validation_file}.py")
            status_code = chan.recv_exit_status()
            self.logger.debug(f"{validation_file} status_code: {status_code}")
            chan.close()
            if status_code == 0:
                successful = successful and True
            else:
                self._errors.append(f"{validation_file} failed ")
                successful = False

        self.logger.debug("deleted uploaded files")
        self.get_drone().cc.cc_helper.ssh_exec_command_without_stdout("rm -rfv ~/validations")

        return self._set_state_based_on_success(successful)
