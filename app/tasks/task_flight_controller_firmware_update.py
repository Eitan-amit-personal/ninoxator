#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
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

from app.helpers.uploader import ports_to_try, firmware, find_bootloader, uploader
from app.tasks.task_interface import TaskInterface


class FlightControllerFirmwareUpdateTask(TaskInterface):

    def __init__(self, drone=None, drone_id=None, local_file=None, version=None):
        super().__init__(drone=drone)
        self.firmware_file = local_file
        self.port = None
        self._version = None
        self.connection_string = None
        self._procedure_name = "Flight Controller Firmware Update"

        self.set_task_status_ready()

    @property
    def version(self):
        return self._version

    def _go_internal(self) -> bool:
        # Load the firmware file
        fw = firmware(self.firmware_file)
        self.logger.info("Loaded firmware for %x,%x, size: %d bytes, waiting for the bootloader..." % (
            fw.property('board_id'), fw.property('board_revision'), fw.property('image_size')))
        print('If the board does not respond within 1-2 seconds, unplug and re-plug the USB connector')
        successful = False
        # create an uploader attached to the port
        while True:
            for port in ports_to_try():
                self.logger.info(f'Trying port {port}')
                try:
                    up = uploader(port, 115200, [57600], None, None, None, 255, 0)
                except Exception as e:
                    self.logger.error(f'Exception {e}')
                    continue
                if find_bootloader(up, port) is False:
                    self.logger.debug('Could not find boot loader')
                    continue

                try:
                    # ok, we have a bootloader, try flashing it
                    up.upload(fw, force=False, boot_delay=None)
                    successful = True
                except RuntimeError as ex:
                    # print the error
                    self.logger.error(ex)
                    successful = False
                    self.logger.error(f'{ex.args}')
                except IOError as ex:
                    successful = False
                    up.close()
                    self.logger.error(ex)
                finally:
                    # always close the port
                    up.close()

                    return successful
