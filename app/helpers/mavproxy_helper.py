#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
# __author__ = "Itay Godasevich"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import os
import sys
import pexpect
import pexpect.popen_spawn

from app.helpers.debug_helper import verbose_mode

FOUND_EXPECTED_VALUE = 0
MAVPROXY_STARTUP_WAIT_TIME = 5


class MavProxyHelperError(Exception):
    def __init__(self, message: str = "Mavproxy Error"):
        self.message = message
        super().__init__(self.message)


class MPHelper:
    _mavproxy = None
    _is_logfile_stdout: bool = False

    def __init__(self, conn_string: str, log_mp_output: bool = False):
        self.conn_string = conn_string
        self.log_mp_output = log_mp_output

    def spawn_mavproxy_proc(self, logfile_path: str = "") -> bool:
        command = f"mavproxy.py --master={self.conn_string}"
        success = False
        try:
            if os.name == 'nt':
                self._mavproxy = pexpect.popen_spawn.PopenSpawn(command, timeout=30, encoding="utf-8")
            else:
                self._mavproxy = pexpect.spawn(command, timeout=30, encoding="utf-8")
            self._mavproxy.expect("online system 1", timeout=30)
            if self.log_mp_output:
                if logfile_path != "":
                    self._mavproxy.logfile = open(logfile_path, "w")
                elif verbose_mode():
                    self._mavproxy.logfile = sys.stdout
                else:
                    self._mavproxy.logfile = None

            self.log_mp_output = self.log_mp_output
            self._is_logfile_stdout = logfile_path == "" and self.log_mp_output
            self._mavproxy.delaybeforesend = 2
            success = True

        except pexpect.ExceptionPexpect as err:
            raise MavProxyHelperError(
                "Could not spawn mavproxy subprocess: {}".format(err)
            )
        return success

    def send_command(self, command: str, expect: str) -> bool:
        if self._mavproxy:
            sent = False
            try:
                self.flush_buffer()
                self._mavproxy.sendline(command)
                result = self._mavproxy.expect(expect)
                if result == FOUND_EXPECTED_VALUE:
                    sent = True
            except pexpect.ExceptionPexpect as err:
                raise MavProxyHelperError(
                    "Could not send command ({}) to subprocess: {}".format(command, err)
                )
            return sent
        else:
            raise MavProxyHelperError(
                "No Mavproxy subprocess has been spawned. Use MPHelper.spawn_mavproxy_proc()."
            )

    def flush_buffer(self):
        if self._mavproxy:
            self._mavproxy.expect(pexpect.TIMEOUT, timeout=0)
        else:
            raise MavProxyHelperError(
                "No Mavproxy subprocess has been spawned. Use MPHelper.spawn_mavproxy_proc()."
            )

    def close_mavproxy(self) -> bool:
        closed = False
        if not self._is_logfile_stdout and self.log_mp_output:
            self._mavproxy.logfile.close()

        try:
            self._mavproxy.close(force=True)
            closed = True
        except Exception:
            pass

        return closed
