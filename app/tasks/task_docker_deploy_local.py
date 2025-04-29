#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2024
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
from datetime import datetime

from app.configurations.config import VISION_COMPUTER_IP_ADDRESS
from ninox_common.ssh_helper import SSHHelper
from ninox_common.vision_computer_helper import USERNAME, PASSWORD
from app.tasks.task_interface import TaskInterface

LOCAL_REGISTRY_IP = '192.168.137.1'
LOCAL_REGISTRY_PORT = 5000


class DockerDeployLocalTask(TaskInterface):
    def __init__(self, drone=None, local_file=None, version=None, run_cmd='', container_url=''):
        super().__init__(drone=drone)
        self.__ssh = SSHHelper(VISION_COMPUTER_IP_ADDRESS, USERNAME, PASSWORD)
        self._prerequisite_pingable_ip = VISION_COMPUTER_IP_ADDRESS
        self._prerequisite_drone_id = False
        self._procedure_name = "Docker Deploy Task"
        self.container_path = local_file  # path to container image
        self.container_version = version
        self.container_url = container_url
        self._run_cmd = run_cmd
        if self.container_version is None:
            self.container_version = 'latest'
        self.logger.info(f"docker deploy local file name: {local_file} container url: {self.container_url}")
        if '/' in local_file:
            self.container_name = local_file.rsplit('/', 1)[-1].replace(".tar.gz",
                                                                        "")  # string after the last slash is the name
        else:
            self.container_name = local_file.replace(".tar.gz", "")

        self.container_name = self.container_name.replace("-docker", "")

    def _go_internal(self) -> bool:

        self.set_task_status_in_progress()
        self.logger.info("Docker Deploy Local Task go")
        succeeded = True
        # transfer docker image to drone
        try:
            self.set_task_status(step="Uploading compressed docker image to vision computer...")
            succeeded = succeeded and self.__ssh.upload_file(self.container_path, f"{self.container_name}.tar.gz")

            self.set_task_status(step="Stopping target container")
            self.logger.info(
                f"Docker container stop output: {self._drone.vc.ssh_exec(f'docker container stop {self.container_name}')}")

            # remove container
            self.set_task_status(step="Removing target container")
            self._drone.vc.ssh_exec(f'docker container rm {self.container_name}')

            # update target computer date to current
            date_time_str = datetime.now().strftime('%Y%m%d %H:%M:%S')
            self._drone.vc.ssh_exec(f'date -s "{date_time_str}"')

            # load the image
            self.set_task_status(step="Unpacking image on vision computer...")
            self._drone.vc.ssh_exec(f"docker load --input {self.container_name}.tar.gz")

            # tag the image
            self._drone.vc.ssh_exec(
                f'docker tag {self.container_url}:{self.container_version} {LOCAL_REGISTRY_IP}:{LOCAL_REGISTRY_PORT}/{self.container_name}:latest')

            # run the container so that docker-runner stores its id for later restarts
            self.set_task_status(step="Executing run newly-deployed container")
            self._drone.vc.ssh_exec(self._run_cmd)

            # clean up tar gz
            self._drone.vc.ssh_exec(f"rm -rf {self.container_name}.tar.gz")

        except Exception as e:
            self.logger.error(f"Error occurred: {e}")
            succeeded = False

        return self._set_state_based_on_success(succeeded)
