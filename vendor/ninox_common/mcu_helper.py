#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2022
# All rights reserved.
#
# __author__ = "Roie Geron"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
import glob
import pathlib

from ninox_common.configuration import DRONE_TMP_DIR
from ninox_common.ssh_helper import SSHHelper

UTILITY_FILE_NAME = 'teensy_loader_cli'


def update_mcu(ssh_helper: SSHHelper, utility_file_path, image_file_path, mcu='TEENSY40', verbose=False,
               tmp_dir=DRONE_TMP_DIR):
    image_file_name = pathlib.Path(image_file_path).name
    firmware_update_command = f'cd {tmp_dir} ; export LD_LIBRARY_PATH={tmp_dir}; ./{UTILITY_FILE_NAME} --mcu={mcu} -s -w {image_file_name} -v'
    success: bool = True
    success = success and ssh_helper.ssh_exec_command_without_stdout(f"mkdir -p {tmp_dir}")
    for file in glob.glob(f'{utility_file_path}/*'):
        success = success and ssh_helper.upload_file(file, f'{tmp_dir}/{pathlib.Path(file).name}')
        success = success and ssh_helper.ssh_exec_command_without_stdout(f'chmod u+x {tmp_dir}/{pathlib.Path(file).name}')
    ssh_helper.upload_file(image_file_path, f'{tmp_dir}/{image_file_name}')
    if success:
        output = ssh_helper.ssh_exec_command(firmware_update_command, verbose)
        success = 'Booting' in output

    return success
