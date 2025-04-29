#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
# All rights reserved.
#
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################

import os
from abc import ABC
from time import sleep

from ninox_common import ninoxator_api_helper
from selenium import webdriver
from selenium.webdriver.common.by import By

from app.configurations.config import COMMUNICATION_DEVICE_IP, PROJECT_DIRECTORY, win
from app.helpers.global_parameters_helper import get_drone_id
from app.tasks.task_interface import TaskInterface

if win:
    from selenium.webdriver.edge.service import Service
    from webdriver_manager.microsoft import EdgeChromiumDriverManager as DriveManager
    from selenium.webdriver.edge.options import Options
else:
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    from webdriver_manager.firefox import GeckoDriverManager as DriveManager


class MicrohardAbstract(TaskInterface, ABC):
    def __init__(self, drone=None):
        super().__init__(drone=drone)
        self._prerequisite_pingable_ip = COMMUNICATION_DEVICE_IP
        service = Service(executable_path=DriveManager().install())
        options = Options()
        options.headless = True
        if win:
            self.driver = webdriver.Edge(service=service, options=options)
        else:
            self.driver = webdriver.Firefox(service=service, options=options)

    def can_connect(self):
        ans = None
        try:
            self._maintenance_page()
            ans = True
        except Exception:
            ans = False

        self.driver.close()
        return ans

    def _maintenance_page(self):
        self.driver.get(f"http://admin:Spear4010@{COMMUNICATION_DEVICE_IP}/cgi-bin/webif/system-upgrade.sh")

    def _sleep_until_in_summary(self):  # when updates are finished driver is redirected to summary page
        while not self._is_in_summary():
            sleep(5)

    def _is_in_summary(self) -> bool:
        try:
            self.driver.find_element(By.NAME, "refreshstop")
        except Exception:
            return False

        return True

    def _postback(self, params):
        ninoxator_api_helper.ninoxator_postback(params, drone_id=get_drone_id())

    def _absolute_path(self, relative_path):
        if win:
            return f"{PROJECT_DIRECTORY}/{relative_path}".replace('/', '\\')
        else:
            return f"{PROJECT_DIRECTORY}/{relative_path}".replace('\\', '/')


class MicrohardFirmware(MicrohardAbstract):
    def __init__(self, drone, microhard_firmware_file):
        super().__init__(drone=drone)
        self._procedure_name = "Microhard Flash"
        self.__microhard_firmware_file = microhard_firmware_file
        self.set_task_status_in_progress()

    def _go_internal(self) -> bool:
        self._maintenance_page()
        configfile = self.driver.find_element(By.NAME, "upgradefile")
        configfile.send_keys(self._absolute_path(self.__microhard_firmware_file))
        sleep(0.1)
        self.driver.find_element(By.NAME, "upgrade").click()
        self._sleep_until_in_summary()
        success = self._set_state_based_on_success(True)
        if success:
            self._postback({'microhard_firmware_filename': os.path.basename(self.__microhard_firmware_file),
                            'microhard_firmware_date': ninoxator_api_helper.datetime_utc_now()})
        return success


class MicrohardParameters(MicrohardAbstract):
    def __init__(self, drone, microhard_parameters_file):
        super().__init__(drone=drone)
        self._procedure_name = "Microhard Parameters"
        self.__microhard_parameters_file = microhard_parameters_file
        self.set_task_status_in_progress()

    def _go_internal(self) -> bool:
        self._maintenance_page()
        configfile = self.driver.find_element(By.NAME, "configfile")
        configfile.send_keys(self._absolute_path(self.__microhard_parameters_file))
        # driver.get_screenshot_as_file("1.png")
        sleep(0.1)
        self.driver.find_element(By.NAME, "chkconfig").click()
        # driver.get_screenshot_as_file("2.png")
        self.driver.find_element(By.NAME, "instconfig").click()
        # driver.get_screenshot_as_file("3.png")
        # sleep(60 * 3 + 15)  # web interface has a timer of about 3 minutes and 2 seconds
        self._sleep_until_in_summary()
        # self.driver.close()
        success = self._set_state_based_on_success(True)
        if success:
            self._postback({'microhard_parameters_filename': os.path.basename(self.__microhard_parameters_file),
                            'microhard_parameters_date': ninoxator_api_helper.datetime_utc_now()})
        return success
