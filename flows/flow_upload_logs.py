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
import requests
from halo import Halo
import docker
import docker.errors

from app import task_runner
from app.configurations.config import CONNECTION_STRING
from app.drone import Drone
from app.helpers.cli_helper import print_instructions, print_logo, print_success, print_error
from app.tasks.task_docker_deploy import VAULT_ADDRESS, PACKAGES_CREDENTIALS
from app.tasks.task_drone_ping import DronePingTask
from version import get_version


def upload_logs_flow() -> bool:
    print_logo()
    print_instructions(f"Ninoxator version {get_version()}")
    print_instructions("")
    print_instructions('Connect ethernet cables to comm device connector')
    print_instructions('Turn Drone on')

    drone_connector = Drone(CONNECTION_STRING)

    with Halo(text="Waiting for drone to wakeup", spinner='bouncingBar'):
        status = task_runner.execute_task(DronePingTask, drone_connector)
    if not status:
        print_error('Drone is not connected')
    else:
        print_success('Drone ID connected')

        # log in to spearauv github
        headers = {'Accept': 'application/json'}
        r = requests.get(f'{VAULT_ADDRESS}/{PACKAGES_CREDENTIALS}', headers=headers).json()
        if "username" in r and "password" in r:
            client = docker.from_env()
            try:
                client.login(username=r["username"], password=r["password"], registry='ghcr.io')
            except docker.errors.APIError as er:
                print(f'Error - {er}')

        # run log-analysis docker for uploading logs
        with Halo(text="Getting logs from drone", spinner='bouncingBar'):
            client = docker.from_env()
            client.containers.run(image='ghcr.io/spearuav/ninox-companion-log-analyzer:latest',
                                  command='python3 run_log_uploader.py',
                                  detach=False,
                                  auto_remove=True)

    input("Press Enter...")
    return status
