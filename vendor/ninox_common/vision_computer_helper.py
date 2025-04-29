#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2022
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

import hashlib
import os
import yaml
from pathlib import Path
from time import sleep

from ninox_common.configuration import VISION_COMPUTER_IP_ADDRESS
from ninox_common.log import Loggable
from ninox_common.mcu_helper import update_mcu
from ninox_common.ssh_helper import SSHHelper

USERNAME = "spearuav"
PASSWORD = "spear4010"

TAR_FILE_NAME = 'viper-payload-sw.tar.gz'
PYINSTALLER_FILE_NAME = 'vision_computer'
PYINSTALLER_FLASK_FILE_NAME = 'drone-ui-flask-jetson'
VC_HOME_FOLDER = '/mnt/sd/spearuav'
REMOTE_LOGS_PATH = [f"{VC_HOME_FOLDER}/logs/"]
VIDEO_SERVER_DIR = f"{VC_HOME_FOLDER}/ninox-viper-payload-sw"
FLASK_PATH = f"{VC_HOME_FOLDER}/drone-ui/flask"
FLASK_SERVICE_PATH = "/etc/systemd/system"
LOG_FILENAME_PREFIX = 'ninox_viper_payload_sw'
VC_CONFIG_FOLDER = f"{VIDEO_SERVER_DIR}/configuration"
VC_CONFIG_FILE = "config.ini"
VC_CONFIG_HASH_FILE = "config_hash"


class VisionComputerHelper(Loggable):
    __ssh: SSHHelper

    def __init__(self, ip_address=VISION_COMPUTER_IP_ADDRESS, username=USERNAME, password=PASSWORD):
        super().__init__()
        self.__ssh = SSHHelper(ip_address, username, password)

    def update_software_pyinstaller(self, local_file) -> bool:
        success = True
        try:
            success &= self.__ssh.ssh_exec_command_without_stdout(f'rm -rf {VIDEO_SERVER_DIR}')
            success &= self.__ssh.ssh_exec_command_without_stdout(f'mkdir -p {VIDEO_SERVER_DIR}')
            success &= self.__ssh.ssh_exec_command_without_stdout(f'chown -R spearuav {VIDEO_SERVER_DIR}', as_root=True)
            success &= self.__ssh.ssh_exec_command_without_stdout(f'chgrp -R spearuav {VIDEO_SERVER_DIR}', as_root=True)
            remote_file_full_path = f'{VIDEO_SERVER_DIR}/{PYINSTALLER_FILE_NAME}'
            success &= self.__ssh.upload_file(local_file, remote_file_full_path)
            success &= self.__ssh.ssh_exec_command_without_stdout(f"chmod u+x {remote_file_full_path}")
        except Exception as e:
            self.logger.error(f'Exception {e}')
            success = False
        return success

    def update_software(self, local_tar_file) -> bool:
        success = True
        try:
            success &= self.__ssh.ssh_exec_command_without_stdout(f'rm -rf {VIDEO_SERVER_DIR}')
            success &= self.__ssh.ssh_exec_command_without_stdout(f'mkdir -p {VIDEO_SERVER_DIR}')
            success &= self.__ssh.ssh_exec_command_without_stdout(f'chown -R spearuav {VIDEO_SERVER_DIR}', as_root=True)
            success &= self.__ssh.ssh_exec_command_without_stdout(f'chgrp -R spearuav {VIDEO_SERVER_DIR}', as_root=True)
            success &= self.__ssh.upload_file(local_tar_file, f'/tmp/{TAR_FILE_NAME}')
            success &= self.__ssh.ssh_exec_command_without_stdout(f"tar xvf /tmp/{TAR_FILE_NAME} -C {VIDEO_SERVER_DIR}")
            success &= self.__ssh.ssh_exec_command_without_stdout(f"rm /tmp/{TAR_FILE_NAME}")
        except Exception as e:
            self.logger.error(f'Exception {e}')
            success = False
        return success

    def update_drone_ui_flask_pyinstaller(self, local_file: str) -> bool:
        success = True
        try:
            success &= self.__ssh.ssh_exec_command_without_stdout(f'rm -rf {FLASK_PATH}')
            success &= self.__ssh.ssh_exec_command_without_stdout(f'mkdir -p {FLASK_PATH}')
            success &= self.__ssh.ssh_exec_command_without_stdout(f'chown -R spearuav {FLASK_PATH}', as_root=True)
            success &= self.__ssh.ssh_exec_command_without_stdout(f'chgrp -R spearuav {FLASK_PATH}', as_root=True)
            remote_file_full_path = f'{FLASK_PATH}/{PYINSTALLER_FLASK_FILE_NAME}'
            success &= self.__ssh.upload_file(local_file, remote_file_full_path)
            success &= self.__ssh.ssh_exec_command_without_stdout(f"chmod u+x {remote_file_full_path}")
        except Exception as e:
            self.logger.error(f'Exception {e}')
            success = False
        return success

    def remove_drone_ui_flask_service(self) -> bool:
        success = True
        try:
            service_file = f'/etc/systemd/system/{PYINSTALLER_FLASK_FILE_NAME}.service'
            output = self.__ssh.ssh_exec_command(f'ls {service_file}', as_root=True)
            output_lines = output.splitlines()
            if output_lines and output_lines[0].strip('\n') == service_file:
                self.stop_drone_ui_flask()
                success &= self.disable_drone_ui_flask()
                success &= self.__ssh.ssh_exec_command_without_stdout(f'rm {service_file}', as_root=True)
                success &= self.reload_daemon()
        except Exception as e:
            self.logger.error(f'Exception {e}')
            success = False
        return success

    def update_drone_ui_flask_service(self, local_file: str) -> bool:
        success = True
        try:
            self.stop_drone_ui_flask()
            success &= self.__ssh.upload_file(local_file, f'/tmp/{PYINSTALLER_FLASK_FILE_NAME}.service')
            success &= self.__ssh.ssh_exec_command_without_stdout(
                f'cp /tmp/{PYINSTALLER_FLASK_FILE_NAME}.service /etc/systemd/system', as_root=True)
            success &= self.__ssh.ssh_exec_command_without_stdout(
                f'rm /tmp/{PYINSTALLER_FLASK_FILE_NAME}.service', as_root=True)
            success &= self.reload_daemon()
            if success:
                sleep(2)
            success &= self.enable_drone_ui_flask()
            success &= self.start_drone_ui_flask()
        except Exception as e:
            self.logger.error(f'Exception {e}')
            success = False
        return success

    def stop_drone_ui_flask(self) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout(
            f'systemctl stop {PYINSTALLER_FLASK_FILE_NAME}', as_root=True)

    def start_drone_ui_flask(self) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout(
            f'systemctl start {PYINSTALLER_FLASK_FILE_NAME}', as_root=True)

    def restart_drone_ui_flask(self) -> bool:
        status = self.__ssh.ssh_exec_command_without_stdout(
            f'systemctl restart {PYINSTALLER_FLASK_FILE_NAME}', as_root=True)
        sleep(2)
        return status

    def enable_drone_ui_flask(self) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout(
            f'systemctl enable {PYINSTALLER_FLASK_FILE_NAME}', as_root=True)

    def disable_drone_ui_flask(self) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout(
            f'systemctl disable {PYINSTALLER_FLASK_FILE_NAME}', as_root=True)

    def reload_daemon(self) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout('systemctl daemon-reload', as_root=True)

    def get_logs(self, dest_folder='./logs', log_filename_prefix=LOG_FILENAME_PREFIX) -> list:
        downloaded_files = []
        for log_dir in REMOTE_LOGS_PATH:
            try:
                files = self.__ssh.list_files_in_directory(log_dir)
                for logfile in files:
                    if log_filename_prefix in logfile:
                        filepath = f'{log_dir}/{logfile}'
                        local_path = f'{dest_folder}/{logfile}'
                        self.__ssh.download_file(filepath, local_path)
                        downloaded_files.append(local_path)
            except FileNotFoundError:
                pass
        return downloaded_files

    def update_mcu_gimbal(self, utility_file_path, image_file_path, verbose=False, mcu='TEENSY40') -> bool:
        return update_mcu(self.__ssh, utility_file_path, image_file_path, mcu, verbose)

    def is_mcu_gimbal_device_exists(self) -> bool:
        output = self.__ssh.ssh_exec_command('udevadm info /dev/tty* | grep ID_VENDOR=Teensyduino')
        return len(output.splitlines()) > 0

    def ssh_exec(self, cmd: str, verbose: bool = False) -> list:
        output = self.__ssh.ssh_exec_command(cmd, verbose, as_root=True)
        return output.splitlines()

    def update_vision_computer_parameters(self, file_path: str) -> bool:
        self.__ssh.ssh_exec_command_without_stdout(f'mkdir -p "{VC_CONFIG_FOLDER}"', as_root=True)
        self.__ssh.ssh_exec_command_without_stdout(f'chown -R spearuav {VC_CONFIG_FOLDER}', as_root=True)
        self.__ssh.upload_file(file_path, f'{VC_CONFIG_FOLDER}/{VC_CONFIG_FILE}')
        return True

    def upload_calibration_files(self, file_list: list) -> bool:
        result = True
        self.__ssh.ssh_exec_command_without_stdout(f'mkdir -p "{VC_CONFIG_FOLDER}"', as_root=True)
        self.__ssh.ssh_exec_command_without_stdout(f'chown -R spearuav {VC_CONFIG_FOLDER}', as_root=True)
        for file in file_list:
            local_file_name = Path(file).name
            result &= self.__ssh.upload_file(file, f'{VC_CONFIG_FOLDER}/{local_file_name}')
        return result

    def sign_config_file_hash(self) -> bool:
        if self.__ssh.is_file_exists(f'{VC_CONFIG_FOLDER}/{VC_CONFIG_FILE}'):
            with self.__ssh.open_file(f'{VC_CONFIG_FOLDER}/{VC_CONFIG_FILE}') as file:
                config_content = file.read()
                config_sha = hashlib.sha256(config_content).hexdigest()
                self.__ssh.ssh_exec_command_without_stdout(
                    f'echo "{config_sha}" > {VC_CONFIG_FOLDER}/{VC_CONFIG_HASH_FILE}', as_root=True)
                return True
        return False

    def upload_file(self, local_path: str, target_path: str):
        file_name = os.path.basename(local_path)
        self.__ssh.upload_file(local_path, f'/tmp/{file_name}')
        self.__ssh.ssh_exec_command_without_stdout(f"mkdir -p {target_path}", as_root=True)
        self.__ssh.ssh_exec_command_without_stdout(f"mv -f /tmp/{file_name} {target_path}", as_root=True)
        self.__ssh.ssh_exec_command_without_stdout(f"chmod u+x {target_path}/{file_name}", as_root=True)

    def get_all_configuration_files_list(self):
        output = self.__ssh.ssh_exec_command(f'ls {VC_CONFIG_FOLDER}')
        return output.splitlines()

    def read_remote_config_yaml_file(self, file_name):
        remote_file_path = f"{VC_CONFIG_FOLDER}/{file_name}"
        local_temp_path = os.path.join("/tmp", file_name)
        yaml_content = None
        try:
            self.__ssh.download_file(remote_file=remote_file_path, local_file=local_temp_path)
            with open(local_temp_path, 'r') as f:
                try:
                    yaml_content = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    self.logger.error(f"Error parsing {local_temp_path}: {e}")
            os.remove(local_temp_path)
        except FileNotFoundError:
            pass
        return yaml_content

    def reboot_computer(self):
        self.__ssh.ssh_exec_command_without_stdout("reboot", as_root=True)
