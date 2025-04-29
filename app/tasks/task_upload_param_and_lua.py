#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2025
# All rights reserved.
#
# __author__ = "Eitan Amit"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import os
import time
import subprocess

from ninox_common.log import Loggable
from app.tasks.task_interface import TaskInterface
from app.drone import Drone

REMOTE_PATH = "/root/drone-technician-server"
FASTAPI_PORT = 8000

class UploadParamAndLuaTask(TaskInterface, Loggable):
    def __init__(self, drone: Drone):
        super().__init__(drone=drone)
        self._procedure_name = "UploadParamAndLuaTask"
        self._remote_ip = drone.cc.get_ip()
        self._scp_target = f"root@{self._remote_ip}:/root"
        self._param_path = None
        self._lua_path = None

    def _find_files(self):
        """Search for .param and .lua files in the release folder"""
        release_folder = self.drone.cc.get_current_local_release_path()
        for fname in os.listdir(release_folder):
            if fname.endswith(".param"):
                self._param_path = os.path.join(release_folder, fname)
            elif fname.endswith(".lua"):
                self._lua_path = os.path.join(release_folder, fname)
        if not self._param_path:
            raise FileNotFoundError("No .param file found in release folder")
        if not self._lua_path:
            raise FileNotFoundError("No .lua file found in release folder")

    def _build_package(self):
        """Run make_offline_package.sh inside the submodule"""
        script_path = "./drone-technician-server/scripts/make_offline_package.sh"
        if not os.path.exists(script_path):
            raise FileNotFoundError("make_offline_package.sh not found in submodule")
        subprocess.check_call([script_path], shell=True)

    def _upload_package(self):
        subprocess.check_call(["scp", "drone-technician-server.tar.gz", self._scp_target])

    def _extract_and_install(self):
        cmd = (
            f"ssh root@{self._remote_ip} \""
            f"mkdir -p {REMOTE_PATH} && cd {REMOTE_PATH} && "
            f"mv /root/drone-technician-server.tar.gz . && "
            f"tar -xzf drone-technician-server.tar.gz && "
            f"chmod +x scripts/setup_drone_technician.sh && "
            f"sudo ./scripts/setup_drone_technician.sh\""
        )
        subprocess.check_call(cmd, shell=True)

    def _post_files(self):
        import requests
        url_base = f"http://{self._remote_ip}:{FASTAPI_PORT}"

        # Wait for FastAPI server
        for _ in range(30):
            try:
                res = requests.get(f"{url_base}/health")
                if res.status_code == 200:
                    break
            except Exception:
                time.sleep(1)
        else:
            raise RuntimeError("FastAPI server not responding")

        # Upload param file
        res = requests.post(f"{url_base}/update_parameters", json={"param_file_path": self._param_path})
        if res.status_code != 200:
            raise RuntimeError("Failed to upload parameters")

        # Upload Lua script
        with open(self._lua_path, 'rb') as f:
            files = {'file': (os.path.basename(self._lua_path), f)}
            res = requests.post(f"{url_base}/upload_lua_script", files=files)
        if res.status_code != 200:
            raise RuntimeError("Failed to upload Lua script")

        # Enable scripting
        res = requests.post(f"{url_base}/set_parameter", json={"name": "SCR_ENABLE", "value": 1})
        if res.status_code != 200:
            raise RuntimeError("Failed to enable scripting")

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        try:
            self._find_files()
            self._build_package()
            self._upload_package()
            self._extract_and_install()
            self._post_files()
            return self._set_state_based_on_success(True)
        except Exception as e:
            self.logger.exception("UploadParamAndLuaTask failed")
            print(str(e))
            return self._set_state_based_on_success(False)