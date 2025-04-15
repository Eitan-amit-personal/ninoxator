#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
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
import serial
import serial.tools.list_ports
from ninox_common.log import get_logger

from app.helpers.serial_helper import ports_to_try

logger = get_logger(__name__)


class NfcSerialWrapper:
    def __init__(self):
        self.connection_string = None
        self.s = None
        self.prompt = b"Spearuav>"
        self.__find_port()

    def read_json(self):
        self.__send_cmd("nfc mode read")
        self.__read_until_prompt()
        if self.s is not None:
            return self.s.readline().decode().strip()
        else:
            return ''

    def write_json(self, json_string):
        self.__write_mode()
        self.__send_cmd(f"nfc write {json_string}")
        self.__read_until_prompt()
        self.__send_cmd("nfc mode read")

    def validate(self, json_string):
        nfc_line = self.read_json()
        success = nfc_line == json_string
        return success

    def __write_mode(self):
        self.__send_cmd("nfc mode write")
        self.__read_until_prompt()

    def __send_cmd(self, cmd):
        if self.s is not None:
            self.s.write(f"{cmd}\r".encode())

    def __read_until_prompt(self):
        all_str = b""

        if self.s is None:
            return all_str

        while True:
            x = self.s.read()
            if not x:
                break
            all_str += x
            if all_str.find(self.prompt, 1) >= 0:
                return all_str
        return all_str

    def __find_port(self):
        for port in ports_to_try({'STLink'}):
            try:
                self.s = serial.Serial(port=port, baudrate=115200, timeout=10)
                self.__send_cmd("help")
                if self.__read_until_prompt().find(self.prompt) >= 0:
                    return
            except Exception:
                self.connection_string = None
                self.s = None


def read_json_from_nfc():
    a = NfcSerialWrapper()
    return a.read_json()


def write_json_to_nfc(json_str: str):
    a = NfcSerialWrapper()
    return a.write_json(json_str)


def validate_json_on_nfc(json_str: str):
    a = NfcSerialWrapper()
    return a.validate(json_str)


if __name__ == '__main__':
    print(read_json_from_nfc())
