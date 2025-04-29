#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
# __author__ = "Tzuriel Lampner"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import os
from time import sleep
from app.tasks.task_interface import TaskInterface
from app.helpers.mavproxy_helper import MavProxyHelperError, MPHelper

DEFAULT_CONNECTION_STRING = "udp:0.0.0.0:20002"


class ArdupilotLuaScriptTask(TaskInterface):
    def __init__(
        self,
        drone=None,
        drone_id=None,
        local_file=None,
        version=None,
        conn_string=DEFAULT_CONNECTION_STRING,
    ):
        super().__init__(drone=drone)
        self._procedure_name = "Ardupilot-Lua-Script-Task"
        self._local_image_file = local_file
        self.set_task_status_ready()
        self.conn_string = conn_string

    def _go_internal(self) -> bool:
        if os.name == 'nt':
            print("Cannot run mavproxy on windows, skipping task")
            success = True
            return self._set_state_based_on_success(success)

        success = False
        self.set_task_status_in_progress()
        self.logger.info("ArdupilotLuaScriptTask go")

        self.set_task_status(step="Connection flight controller")
        mavproxy_helper = MPHelper(self.conn_string, log_mp_output=True)
        mavproxy_helper.spawn_mavproxy_proc()
        sleep(10)
        self.set_task_status(step="Removing old LUA script")

        # we don't care if we fail these, they're here just in case the dirs don't exist
        try:
            mavproxy_helper.send_command("ftp rm APM\\scripts\\AP.lua", "")
            mavproxy_helper.send_command("ftp mkdir APM\\scripts", "")
        except MavProxyHelperError as err:
            self.logger.info(f"Could not send command: {err}")

        # put file
        self.set_task_status(step="Uploading new LUA script")
        try:
            mavproxy_helper.flush_buffer()
            file_len = os.path.getsize(self._local_image_file)
            result = mavproxy_helper.send_command(
                f"ftp put {self._local_image_file} APM\\scripts\\AP.lua", f"{file_len}"
            )
            if result is True:
                # double check that the file exists in the dir
                exists_in_dir = mavproxy_helper.send_command(
                    "ftp list APM\\scripts", f"AP.lua	{file_len}"
                )
                if exists_in_dir is True:
                    success = True
                    if mavproxy_helper.close_mavproxy():
                        self.logger.info("Closed _mavproxy spawn")
                    else:
                        self.logger.critical("Error closing _mavproxy spawn")
                else:
                    self.logger.critical("AP.lua not found in APM\\scripts")
            else:
                self.logger.critical(f"Could not send file {self._local_image_file}")
        except MavProxyHelperError as err:
            self.logger.critical(f"Could not send ftp put command: {err}")

        return self._set_state_based_on_success(success)
