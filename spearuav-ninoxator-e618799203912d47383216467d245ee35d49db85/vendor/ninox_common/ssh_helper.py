#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2022
# All rights reserved.
#
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################

import paramiko
from paramiko.client import SSHClient
from paramiko.config import SSH_PORT
from paramiko.sftp_client import SFTPClient
from ninox_common.log import Loggable

MAX_SSH_CONNECT_TRIES = 5


class SSHHelper(Loggable):
    __ssh: SSHClient
    __sftp_client: SFTPClient

    def __init__(self, host_ip_address, username, password):
        super().__init__()
        self.__ssh = None
        self.__sftp_client = None
        self.host_ip = host_ip_address
        self.username = username
        self.password = password
        self.port = SSH_PORT

    def __del__(self):
        self.close_connections()

    def ssh_is_active(self):
        self.logger.debug("ssh is active")
        try:
            if self.__ssh is not None and self.__ssh.get_transport() is not None:
                return self.__ssh.get_transport().is_active()
        except Exception as e:
            self.logger.debug(e)

        return False

    def mkdir_p(self, remote_path):
        self.__sftp_init()
        dir_path = str()
        for dir_folder in remote_path.split("/"):
            if dir_folder == "":
                continue
            dir_path += r"/{0}".format(dir_folder)
            try:
                self.__sftp_client.listdir(dir_path)
            except IOError:
                self.__sftp_client.mkdir(dir_path)

    def is_file_exists(self, file_full_path):
        self.__sftp_init()
        try:
            self.__sftp_client.stat(file_full_path)
            return True
        except Exception as e:
            self.logger.debug(e)
            return False

    def upload_file(self, local_file, remote_file):
        self.__sftp_init()
        self.__sftp_client.put(local_file, remote_file)
        return True

    def delete_file(self, file_full_path):
        self.__sftp_init()
        status = True
        try:
            self.__sftp_client.remove(file_full_path)
        except FileNotFoundError:
            pass

        return status

    def download_file(self, remote_file, local_file):
        self.__sftp_init()
        self.__sftp_client.get(remote_file, local_file)

    def read_file(self, file_full_path):
        self.__sftp_init()
        try:
            with self.__sftp_client.open(file_full_path) as file:
                return file.read().decode()
        except FileNotFoundError:
            return None

    def write_file(self, data, filename):
        self.__sftp_init()
        try:
            with self.__sftp_client.open(filename, 'w') as file:
                file.write(data)
                file.flush()
                return True
        except IOError as e:
            self.logger.error(f"Error writing file {filename} : {e}")

        return False

    def build_ssh_cmd(self, cmd, as_root=False) -> str:
        if as_root is True:
            cmd = f'echo {self.password} | sudo -S {cmd}'
        return cmd

    def ssh_exec_command_without_stdout(self, cmd, as_root=False):
        self.__ssh_init()
        stdin, stdout, stderr = self.__ssh.exec_command(self.build_ssh_cmd(cmd, as_root))
        return stdout.channel.recv_exit_status() == 0

    def ssh_exec_command(self, cmd, verbose=False, as_root=False) -> str:
        output = ""
        self.__ssh_init()
        stdin, stdout, stderr = self.__ssh.exec_command(self.build_ssh_cmd(cmd, as_root))
        if verbose:
            while not stdout.channel.exit_status_ready():
                while stdout.channel.recv_ready():
                    byte = stdout.channel.recv(1)  # Read 1 byte at a time
                    ch = byte.decode('utf-8')
                    output += ch
                    print(ch, end='', flush=True)  # Print each byte immediately
        else:
            output = stdout.read().decode('utf-8')
        return output

    def open_session(self):
        self.__ssh_init()
        return self.__ssh.get_transport().open_session()

    def list_files_in_directory(self, directory, filter_str=None):
        self.__sftp_init()
        result = self.__sftp_client.listdir(directory)
        if filter_str is not None:
            result = list(filter(lambda filename: filter_str in filename, result))
        return result

    def close_connections(self):
        if self.__ssh is not None:
            self.__ssh.close()

    def __ssh_init(self):
        if self.__ssh is not None and self.ssh_is_active():
            return

        for i in range(MAX_SSH_CONNECT_TRIES):
            try:
                self.__ssh = paramiko.SSHClient()
                self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.__ssh.connect(self.host_ip, self.port, self.username, self.password)
                if self.ssh_is_active():
                    break
            except Exception as e:
                self.logger.debug(e)

    def __sftp_init(self):
        self.__ssh_init()
        if self.__sftp_client is None:
            self.__sftp_client = self.__ssh.open_sftp()

    def open_file(self, filename, mode='r'):
        self.__ssh_init()
        return self.__sftp_client.open(filename, mode)
