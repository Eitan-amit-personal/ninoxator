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

import configparser
import glob
import hashlib
import json
import pathlib
import os
from json import JSONDecodeError
from time import sleep
from paramiko.ssh_exception import SSHException

from ninox_common.configuration import DRONE_IP, DRONE_TMP_DIR, DRONE_INFO_JSON, DRONE_CONFIGURATION_DIR, \
    DRONE_CONFIG_FILE, EFLASH_IMAGES_FILE
from ninox_common.git_wrapper import get_ninox_drone_configuration_file
from ninox_common.log import Loggable
from ninox_common.mcu_helper import update_mcu
from ninox_common.ssh_helper import SSHHelper

USERNAME = "root"
PASSWORD = "fa"
LOG_FILENAME_PREFIX = 'companion'
TAR_FILE_NAME = 'ninox-companion-computer.tar.gz'  # pyinstaller executable
REMOTE_LOGS_PATH = ['companion/logs/', '/var/log/spearuav']
EFLASHER_COMMAND = f"eflasher -i {EFLASH_IMAGES_FILE} --auto-exit"
ON_DRONE_RECIPE_PATH = f"{DRONE_CONFIGURATION_DIR}/recipe.json"
FLASK_PATH = '/root/drone-ui/flask'
DRONE_FLASK_FILE_NAME = 'drone-ui-flask.tar.gz'
CC_CONFIG_FILE = '/root/companion/configuration/config.ini'
CC_CONFIG_HASH_FILE = '/root/companion/configuration/config_hash'
COMPANION_SERVICE = 'dronecompanion'
MODEMMANAGER_SERVICE = 'ModemManager.service'
FLUTTER_SERVICE = 'droneuiflutter'
FLASK_SERVICE_OLD = 'droneuiflask'
FLASK_SERVICE_PYINSTALLER = 'drone-ui-flask-nanopi'
MAVPROXY_SERVICE = 'dronemavproxy'
TELEMETRY_SERVICE = 'dronetelemetry'
SYSTEMD_PATH = '/lib/systemd/system'


class CCHelper(Loggable):
    __ssh: SSHHelper

    def __init__(self, ip_address=DRONE_IP, username=USERNAME, password=PASSWORD):
        super().__init__()
        self.__ssh = SSHHelper(ip_address, username, password)

    def get_pilot_port(self):
        output = self.__ssh.ssh_exec_command("ls /dev/serial/by-id/")
        devices = output.splitlines()

        # find mRo devices with interface id 00
        mro_device_path = None
        for device in devices:
            if "mRo" in device and "if00" in device:
                mro_device_path = f"/dev/serial/by-id/{device}"
                break

        # If the found device, get the corresponding /dev/tty* name
        if mro_device_path:
            output = self.__ssh.ssh_exec_command(
                f"udevadm info -q name -n {mro_device_path}")
            tty_device = output.strip()
            return f'/dev/{tty_device}'

        return ''

    def update_ardupilot_firmware(self, image_file_path, verbose=False) -> bool:
        has_mavproxy = self.has_service(MAVPROXY_SERVICE)
        if has_mavproxy:
            self.stop_service(MAVPROXY_SERVICE)
        has_telemetry = self.has_service(TELEMETRY_SERVICE)
        if has_telemetry:
            self.stop_service(TELEMETRY_SERVICE)
        self.stop_service(COMPANION_SERVICE)
        current_path = str(pathlib.Path(__file__).parent.resolve())
        firmware_update_file_path = pathlib.Path(glob.glob(current_path + '/px_uploader.py')[0])
        firmware_update_file_name = pathlib.Path(firmware_update_file_path).name
        image_file_name = pathlib.Path(image_file_path).name
        self.__ssh.ssh_exec_command_without_stdout(f"mkdir -p {DRONE_TMP_DIR}")
        self.stop_service(MODEMMANAGER_SERVICE)
        self.disable_service(MODEMMANAGER_SERVICE)
        self.__ssh.upload_file(firmware_update_file_path, f'{DRONE_TMP_DIR}/{firmware_update_file_name}')
        self.__ssh.upload_file(image_file_path, f'{DRONE_TMP_DIR}/{image_file_name}')
        pilot_port = self.get_pilot_port()
        command = f'cd {DRONE_TMP_DIR} ;python3 {firmware_update_file_name} {image_file_name} --port {pilot_port}'
        output = self.__ssh.ssh_exec_command(command, verbose)
        self.start_service(COMPANION_SERVICE)
        if has_mavproxy:
            self.start_service(MAVPROXY_SERVICE)
        if has_telemetry:
            self.start_service(TELEMETRY_SERVICE)
        return 'Rebooting' in output

    def get_drone_info(self, drone_config_file=DRONE_CONFIG_FILE):
        json_string = self.__ssh.read_file(drone_config_file)
        json_obj = None
        if json_string is not None:
            try:
                json_obj = json.loads(json_string)
            except ValueError:
                json_obj = None
        return json_obj

    def get_launch_count(self) -> int:
        file_content = self.__ssh.read_file(f"{DRONE_CONFIGURATION_DIR}/launch_counter_file.json")
        dic = json.loads(file_content)
        launch_count = dic['launch_counter']

        return launch_count

    def set_drone_id_to_drone_info(self, drone_id: int) -> bool:
        status = self.set_drone_info(drone_id=drone_id)
        return status

    def set_drone_info(self, drone_id=None, software_version=None, hw_version=None, drone_type=None) -> bool:
        drone_info_json = self.get_drone_info(DRONE_CONFIG_FILE)
        if drone_info_json is None:
            drone_info_json = json.loads(get_ninox_drone_configuration_file(DRONE_INFO_JSON))

        new_drone_id = drone_id

        json_obj = drone_info_json
        if drone_id is not None:
            json_obj['serial_number'] = new_drone_id
        if software_version is not None:
            json_obj['drone_version'] = software_version
            json_obj['software_version'] = software_version
        if hw_version is not None:
            json_obj['hw_version'] = hw_version
        if drone_type is not None:
            json_obj['drone_type'] = drone_type

        json_string = json.dumps(json_obj)
        json_string = json_string.strip()
        json_string = json_string.replace(" ", "")

        try:
            self.__ssh.ssh_exec_command_without_stdout(f"mkdir -p {DRONE_CONFIGURATION_DIR}")
            self.__ssh.write_file(json_string, DRONE_CONFIG_FILE)
        except Exception as e:
            self.logger.error(f"set_drone_info {e}")
            return False

        return True

    def set_communication_info(self, device_type: str, frequency: int, network_id: any, mesh_id: int = -1) -> bool:
        config = configparser.ConfigParser()
        try:
            with self.__ssh.open_file(CC_CONFIG_FILE) as file:
                config.read_file(file)
                config['MICROHARD']['type'] = device_type
                config['MICROHARD']['frequency'] = str(frequency)
                config['MICROHARD']['network_id'] = str(network_id)
                if mesh_id != -1:
                    config['MICROHARD']['mesh_id'] = str(mesh_id)
            with self.__ssh.open_file(CC_CONFIG_FILE, mode='w') as file:
                config.write(file)
            success = True
        except (configparser.ParsingError, configparser.NoSectionError, configparser.NoOptionError) as err:
            self.logger.error(f"cannot update comm info in config ini file - {err}")
            success = False

        return success

    def get_drone_id_from_drone_info(self) -> int:
        drone_id = None
        try:
            file_content = self.__ssh.read_file(f"{DRONE_CONFIGURATION_DIR}/{DRONE_INFO_JSON}")
            dic = json.loads(file_content)
            drone_id = dic['serial_number']
        except TypeError:
            self.logger.error("TypeError probably not a json file")
        except KeyError:
            self.logger.error(f"KeyError serial_number not {DRONE_INFO_JSON} file")
            pass
        except JSONDecodeError:
            self.logger.error(f"JSONDecodeError not {DRONE_INFO_JSON} file")

        if drone_id is not None:
            return int(drone_id)
        else:
            return -1

    def get_current_drone_meal(self) -> str:
        my_current_meal = ''
        if self.__ssh.is_file_exists(ON_DRONE_RECIPE_PATH):
            my_current_meal = self.__ssh.read_file(ON_DRONE_RECIPE_PATH)
        return my_current_meal

    def update_meal(self, meal) -> bool:
        return self.__ssh.write_file(meal, ON_DRONE_RECIPE_PATH)

    def reset_meal(self) -> bool:
        return self.__ssh.delete_file(ON_DRONE_RECIPE_PATH)

    def get_config_ini_dic(self) -> dict:
        config_pulled_dic = {}
        try:
            with self.__ssh.open_file(CC_CONFIG_FILE) as file:
                config_pulled_dic = {}
                parser = configparser.ConfigParser()
                parser.read_file(file)
                sections = parser.sections()
                for sec in sections:
                    config_pulled_dic[sec] = {}
                    for k, v in parser.items(sec):
                        if v.isnumeric():
                            config_pulled_dic[sec][k] = int(v)
                        elif v.lower() == 'true':
                            config_pulled_dic[sec][k] = True
                        elif v.lower() == 'false':
                            config_pulled_dic[sec][k] = False
                        else:
                            config_pulled_dic[sec][k] = v
        except FileNotFoundError:
            self.logger.warn("Can not file ini file, assuming blank drone")

        return config_pulled_dic

    def update_companion(self, local_tar_file) -> bool:
        self.logger.debug(f"update_companion_on_drone({local_tar_file}")
        has_mavproxy = self.has_service(MAVPROXY_SERVICE)
        if has_mavproxy:
            self.stop_service(MAVPROXY_SERVICE)
        has_telemetry = self.has_service(TELEMETRY_SERVICE)
        if has_telemetry:
            self.stop_service(TELEMETRY_SERVICE)
        try:
            self.stop_service(COMPANION_SERVICE)
            self.__ssh.ssh_exec_command_without_stdout('rm -rf companion')
            tar_file_name = TAR_FILE_NAME
            self.__ssh.upload_file(f"{local_tar_file}", tar_file_name)
            self.__ssh.ssh_exec_command_without_stdout(f"tar xvf {tar_file_name}")
            # self.__ssh.ssh_exec_command_without_stdout(
            #     'cat companion/version.py | grep -m 1 VERSION')  # TODO show output
            self.__ssh.ssh_exec_command_without_stdout('chown -R root companion')
            self.__ssh.ssh_exec_command_without_stdout('chgrp -R root companion')
            self.__ssh.ssh_exec_command_without_stdout(f"rm {tar_file_name}")
            self.start_service(COMPANION_SERVICE)
            success = True

        except Exception as e:
            self.logger.error(f'Exception {e}')
            success = False

        return success

    def update_drone_ui_flask(self, local_file) -> bool:
        # stop and disable newer flask service (if exists), and make sure old task is enabled
        self.stop_service(FLASK_SERVICE_PYINSTALLER)
        self.disable_service(FLASK_SERVICE_PYINSTALLER)
        self.enable_service(FLASK_SERVICE_OLD)

        # update flask app
        success = True
        self.stop_service(FLASK_SERVICE_OLD)
        success = success and self.__ssh.ssh_exec_command_without_stdout(f"rm -rf {FLASK_PATH}")
        tar_file_name = DRONE_FLASK_FILE_NAME
        success = success and self.__ssh.upload_file(f"{local_file}", tar_file_name)
        success = success and self.__ssh.ssh_exec_command_without_stdout(f"mkdir {FLASK_PATH}")
        success = success and self.__ssh.ssh_exec_command_without_stdout(f"tar xvf {tar_file_name} -C {FLASK_PATH}")
        success = success and self.__ssh.ssh_exec_command_without_stdout(f"rm {tar_file_name}")
        success = success and self.start_service(FLASK_SERVICE_OLD)
        return success

    def update_drone_ui_flask_pyinstaller(self, local_file: str) -> bool:
        success: bool = True
        try:
            success = success and self.__ssh.ssh_exec_command_without_stdout(f'rm -rf {FLASK_PATH}')
            success = success and self.__ssh.ssh_exec_command_without_stdout(f'mkdir -p {FLASK_PATH}')
            remote_file_full_path = f'{FLASK_PATH}/{FLASK_SERVICE_PYINSTALLER}'
            success = success and self.__ssh.upload_file(f"{local_file}", remote_file_full_path)
            success = success and self.__ssh.ssh_exec_command_without_stdout(f"chmod u+x {remote_file_full_path}")

        except Exception as e:
            self.logger.error(f'Exception {e}')
            success = False

        return success

    def update_drone_ui_flask_service(self, local_file: str) -> bool:
        success: bool = True
        try:
            # stop and disable old service
            self.stop_service(FLASK_SERVICE_OLD)
            self.disable_service(FLASK_SERVICE_OLD)

            # update new service
            self.stop_service(FLASK_SERVICE_PYINSTALLER)
            success = success and self.__ssh.upload_file(local_file,
                                                         f'{SYSTEMD_PATH}/{FLASK_SERVICE_PYINSTALLER}.service')
            success = success and self.reload_daemon()
            if success:
                sleep(2)
            success = success and self.enable_service(FLASK_SERVICE_PYINSTALLER)
            success = success and self.start_service(FLASK_SERVICE_PYINSTALLER)

        except Exception as e:
            self.logger.error(f'Exception {e}')
            success = False

        return success

    def update_drone_ui_flutter(self, local_file) -> bool:
        self.stop_service(FLUTTER_SERVICE)
        ui_flutter_dir = '/root/drone-ui/flutter'
        ui_dir = '/root/drone-ui'
        tar_file_name = os.path.basename(local_file)
        self.__ssh.ssh_exec_command_without_stdout(f"rm -rf {ui_flutter_dir}")
        self.__ssh.ssh_exec_command_without_stdout(f"mkdir -p {ui_flutter_dir}")
        self.__ssh.upload_file(local_file, f'{DRONE_TMP_DIR}/{tar_file_name}')
        self.__ssh.ssh_exec_command_without_stdout(f"mv {DRONE_TMP_DIR}/{tar_file_name} {ui_dir}/{tar_file_name}")
        self.__ssh.ssh_exec_command_without_stdout(f"tar xvf {ui_dir}/{tar_file_name} -C {ui_dir}")
        self.__ssh.ssh_exec_command_without_stdout(f"rm {ui_dir}/{tar_file_name}")
        self.start_service(FLUTTER_SERVICE)
        return True  # TODO better check

    def is_service_running(self, service: str) -> bool:
        output = self.__ssh.ssh_exec_command(f"systemctl is-active {service}")
        return output.strip() == 'active'

    def stop_service(self, service: str) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout(f'systemctl stop {service}')

    def start_service(self, service: str) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout(f'systemctl start {service}')

    def restart_service(self, service: str) -> bool:
        status = self.__ssh.ssh_exec_command_without_stdout(f'systemctl restart {service}')
        sleep(2)
        return status

    def reload_daemon(self) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout('systemctl daemon-reload')

    def enable_service(self, service: str) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout(f'systemctl enable {service}')

    def disable_service(self, service: str) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout(f'systemctl disable {service}')

    def remove_service(self, service: str) -> bool:
        return self.__ssh.ssh_exec_command_without_stdout(f'rm -rf {SYSTEMD_PATH}/{service}.service')

    def get_logs(self, dest_folder='./logs', log_filename_prefix=LOG_FILENAME_PREFIX) -> list:
        downloaded_files = []
        for log_dir in REMOTE_LOGS_PATH:
            try:
                files = self.__ssh.list_files_in_directory(log_dir)
                for logfile in files:
                    if log_filename_prefix in logfile:
                        filepath = log_dir + '/' + logfile
                        local_path = dest_folder + "/" + logfile
                        self.__ssh.download_file(filepath, local_path)
                        downloaded_files.append(local_path)
            except FileNotFoundError:
                pass
        return downloaded_files

    def update_mcu_attack(self, utility_file_path, image_file_path, verbose=False, mcu='TEENSY40') -> bool:
        return update_mcu(self.__ssh, utility_file_path, image_file_path, mcu, verbose)

    def flash_companion(self) -> bool:
        output = self.__ssh.ssh_exec_command(EFLASHER_COMMAND)
        return "Finish!" in output

    def is_file_exist(self, filename: str) -> bool:
        return self.__ssh.is_file_exists(filename)

    def is_mcu_attack_device_exists(self) -> bool:
        output = self.__ssh.ssh_exec_command(f'udevadm info /dev/tty* | grep ID_VENDOR=Teensyduino')
        devices = output.splitlines()
        return len(devices) > 0

    def is_mcu_ardupilot_device_exists(self) -> bool:
        # pilot mode is either "mRoCZeroOEMH7" or "mRoControlZeroOEMH7", check for mRoC
        output = self.__ssh.ssh_exec_command(f'udevadm info /dev/tty* | grep ID_MODEL=mRoC')
        devices = output.splitlines()
        return len(devices) > 0

    def update_companion_computer_parameters(self, file_path) -> bool:
        success = False
        try:
            configuration_dir = '~/companion/configuration'
            config_file_name = 'config.ini'
            self.__ssh.upload_file(file_path, f'{DRONE_TMP_DIR}/{config_file_name}')
            self.__ssh.ssh_exec_command_without_stdout(
                f"mv {DRONE_TMP_DIR}/{config_file_name} {configuration_dir}/{config_file_name}")
            success = True
        except FileNotFoundError:
            self.logger.error(f'Cannot upload file {file_path}')
        except SSHException as e:
            self.logger.error(f'Exception {e}')

        return success

    def is_eflasher(self) -> bool:
        # check if machine has the flashing app (i.e. NanoPi eflasher SD card)
        output = self.__ssh.ssh_exec_command("which eflasher")
        output_lines = output.splitlines()
        if len(output_lines) != 0:
            return True

        return False

    def linux_version(self) -> str:
        output = self.__ssh.ssh_exec_command("lsb_release -rs")
        output_lines = output.splitlines()
        return output_lines[0]

    def has_service(self, service_name: str) -> bool:
        cmd = f'test -f {SYSTEMD_PATH}/{service_name}.service && echo "Exists" || echo "Not exists"'
        output = self.__ssh.ssh_exec_command(cmd)
        return output.strip() == 'Exists'

    def install_service(self, service_name: str, service_file_content: str):
        self.stop_service(service_name)
        self.__ssh.write_file(service_file_content, f'{SYSTEMD_PATH}/{service_name}.service')
        self.reload_daemon()
        sleep(2)
        self.enable_service(service_name)

    def pip_install_global(self, package_path: str):
        package_name = os.path.basename(package_path)
        self.__ssh.upload_file(package_path, f'/root/{package_name}')
        self.__ssh.ssh_exec_command_without_stdout(f"pip install /root/{package_name}")
        self.__ssh.ssh_exec_command_without_stdout(f'rm -rf /root/{package_name}')

    def upload_file(self, local_path: str, target_path: str):
        file_name = os.path.basename(local_path)
        self.__ssh.upload_file(local_path, f'{DRONE_TMP_DIR}/{file_name}')
        self.__ssh.ssh_exec_command_without_stdout(f"mkdir -p {target_path}")   # make sure path created
        self.__ssh.ssh_exec_command_without_stdout(f"mv -f {DRONE_TMP_DIR}/{file_name} {target_path}")
        self.__ssh.ssh_exec_command_without_stdout(f"chmod u+x {target_path}/{file_name}")  # allow running permission

    def sign_config_file_hash(self) -> bool:
        if self.__ssh.is_file_exists(CC_CONFIG_FILE):
            with self.__ssh.open_file(CC_CONFIG_FILE) as file:
                config_content = file.read()
                config_sha = hashlib.sha256(config_content).hexdigest()
                self.__ssh.write_file(config_sha, CC_CONFIG_HASH_FILE)
                return True

        return False

    def reboot_computer(self):
        self.__ssh.ssh_exec_command_without_stdout("reboot")
        self.__ssh.close_connections()
