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
import docker
import docker.errors
import requests
from datetime import datetime

from app.configurations.config import VISION_COMPUTER_IP_ADDRESS
from app.tasks.task_interface import TaskInterface
from app.helpers.debug_helper import verbose_mode

PACKAGES_CREDENTIALS = 'github-packages'
VAULT_ADDRESS = 'http://spearuav-ubuntu-server.spearuav:8020/read'
LOCAL_REGISTRY_IP = '192.168.137.1'
LOCAL_REGISTRY_PORT = 5000


class DockerDeployTask(TaskInterface):
    def __init__(self, drone=None, local_file=None, version=None, run_cmd=''):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = VISION_COMPUTER_IP_ADDRESS
        self._prerequisite_drone_id = False
        self.container_path = local_file  # local_file is the url, such as 'ghcr.io/spearuav/vision-computer'
        self.container_version = version
        self._run_cmd = run_cmd
        if self.container_version is None:
            self.container_version = 'latest'
        if '/' in local_file:
            self.container_name = local_file.rsplit('/', 1)[-1]  # string after the last slash is the name
        else:
            self.container_name = local_file
        if self._run_local_registry() is True:  # as a pre-requisite make sure local docker registry is running
            self.set_task_status_ready()
        self._procedure_name = f"Docker Deploy Task - {self.container_name}"

    def _go_internal(self) -> bool:
        self.set_task_status_in_progress()
        self.logger.info("Docker Deploy Task - go")
        succeeded = True
        succeeded = succeeded and self._pull_and_update_local_registry()
        succeeded = succeeded and self._pull_local_docker_onto_target()
        return self._set_state_based_on_success(succeeded)

    def _run_local_registry(self) -> bool:
        succeeded = False
        client = docker.from_env()
        try:
            container = client.containers.get('registry')
            if container.status != "running":
                container.start()
            succeeded = True
        except docker.errors.NotFound:
            client.containers.run('registry',
                                  name='registry',
                                  ports={str(LOCAL_REGISTRY_PORT): str(LOCAL_REGISTRY_PORT)},
                                  detach=True)
        return succeeded

    def _pull_and_update_local_registry(self) -> bool:
        succeeded = False
        headers = {'Accept': 'application/json'}
        r = requests.get(f'{VAULT_ADDRESS}/{PACKAGES_CREDENTIALS}', headers=headers).json()
        if "username" in r and "password" in r:
            client = docker.from_env()
            try:
                self.set_task_status(step="Log in to remote registry container")
                client.login(username=r["username"], password=r["password"], registry='ghcr.io')
                self.set_task_status(step="Pulling container to local host")
                image = client.images.pull(repository=self.container_path,
                                           platform="linux/arm64",
                                           tag=self.container_version)
                self.set_task_status(step="Tagging container as version to be installed")
                # tag it with the container name!
                succeeded = image.tag(f'{LOCAL_REGISTRY_IP}:{LOCAL_REGISTRY_PORT}/{self.container_name}')
                self.set_task_status(step="Pushing container to local registry")
                succeeded = succeeded and client.api.push(
                    f'{LOCAL_REGISTRY_IP}:{LOCAL_REGISTRY_PORT}/{self.container_name}')
            except docker.errors.APIError as er:
                print(f'Error - {er}')
        else:
            print('VAULT error - cannot find credentials for acquiring container')
        return succeeded

    def _pull_local_docker_onto_target(self) -> bool:
        # stop the old container
        self.set_task_status(step="Stopping target container")
        self._drone.vc.ssh_exec(f'docker container stop {self.container_name}')

        # remove container
        self.set_task_status(step="Removing target container")
        self._drone.vc.ssh_exec(f'docker container rm {self.container_name}')

        # update target computer date to current
        date_time_str = datetime.now().strftime('%Y%m%d %H:%M:%S')
        self._drone.vc.ssh_exec(f'date -s "{date_time_str}"')

        # to be on the safe side, search for all dockers of the same repository (i.e. that were not named)
        output_lines = self._drone.vc.ssh_exec(
            f'docker ps -a --filter "ancestor={LOCAL_REGISTRY_IP}:{LOCAL_REGISTRY_PORT}/{self.container_name}" -q')
        for line in output_lines:
            container_id = line.strip('\n')
            self.set_task_status(step=f"Removing lost container with id {container_id}")
            self._drone.vc.ssh_exec(f'docker container stop {container_id}')
            self._drone.vc.ssh_exec(f'docker container rm {container_id}')

        # pull a new docker image
        self.set_task_status(step="Pulling container onto target")
        self._drone.vc.ssh_exec(
            f'docker image pull {LOCAL_REGISTRY_IP}:{LOCAL_REGISTRY_PORT}/{self.container_name}', verbose_mode())

        # run the container so that docker-runner stores its id for later restarts
        self.set_task_status(step="Executing run newly-deployed container")
        self._drone.vc.ssh_exec(self._run_cmd, verbose_mode())

        return True
