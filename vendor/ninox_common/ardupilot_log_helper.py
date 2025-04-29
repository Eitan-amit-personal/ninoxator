#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
# All rights reserved.
#
# __author__ = "Roie Geron"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
import _io
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

from dronekit import Vehicle

from ninox_common.log import get_logger

TARGET_SYSTEM = 0
TARGET_COMPONENT = 0

logger = get_logger(__name__)

my_vehicle: Vehicle = None
download_set: set = set()
download_file: _io.FileIO = None
download_lognum: int = 0
download_filename: str = ''
download_start: int = 0
download_ofs: int = 0
num_logs: int = -1
last_log_num = -1
my_log_folder: str = ''
log_entries = []
is_finished_download: bool = False
download_last_timestamp = None
retries = 0

NUMBER_OF_THREADS_IN_POOL = 1
executor = ThreadPoolExecutor(max_workers=NUMBER_OF_THREADS_IN_POOL)

# using ugly lock for sync need to be changed
lock = threading.Lock()
log_list_lock = threading.Lock()


def default_progress_callback(count_progress, offset, total_size):
    pass


__progress_callback = default_progress_callback


def init(vehicle: Vehicle, log_folder):
    global my_vehicle, my_log_folder
    logger.info(f'Initialize Ardupilot logs download to folder {log_folder}')
    my_vehicle = vehicle
    my_log_folder = log_folder
    my_vehicle.add_message_listener('LOG_ENTRY', __handle_log_entry)
    my_vehicle.add_message_listener('LOG_DATA', __handle_log_data)
    __get_log_list()


def __handle_log_entry(vehicle, name, message):
    global num_logs, last_log_num, log_entries
    """handling incoming log entry"""
    if message.time_utc == 0:
        tstring = ''
    else:
        tstring = time.ctime(message.time_utc)
    num_logs = message.num_logs
    last_log_num = message.last_log_num
    if message.num_logs == 0:
        logger.info("No logs")
        lock.release()
        return
    log_entries.append(message)
    logger.info("Log %u numLogs %u lastLog %u size %u %s" % (message.id, message.num_logs, message.last_log_num,
                                                             message.size, tstring))
    if message.id == message.last_log_num:
        log_list_lock.release()


def __handle_log_data(vehicle, name, message):
    global download_file, download_ofs, download_set, download_filename, is_finished_download, download_last_timestamp
    """handling incoming log data"""
    if download_file is None:
        logger.info("Download file is None")
        lock.release()
        return
    logger.debug(f'get {message.count} bytes , {message.ofs} offset')
    if message.ofs != download_ofs:
        download_file.seek(message.ofs)
        download_ofs = message.ofs
    if message.count != 0:
        s = bytearray(message.data[:message.count])
        download_file.write(s)
        download_set.add(message.ofs // 90)
        download_ofs += message.count
        if __progress_callback is not None:
            __progress_callback(message.count, download_ofs, log_entries[message.id - 1].size)
    download_last_timestamp = time.time()
    if message.count == 0 or (message.count < 90 and len(download_set) == 1 + (message.ofs // 90)):
        dt = time.time() - download_start
        download_file.close()
        size = os.path.getsize(download_filename)
        speed = size / (1000.0 * dt)
        logger.info(f"Finished download file {download_filename} size {size} bytes {dt:.1f} seconds "
                    f"speed {speed:.1f} kByte/sec")
        download_file = None
        download_filename = ''
        download_set = set()
        __log_request_end_send()
        lock.release()


def handle_log_data_missing():
    global retries
    '''handling missing incoming log data'''
    if len(download_set) == 0:
        return
    highest = max(download_set)
    diff = set(range(highest)).difference(download_set)
    if len(diff) == 0:
        __log_request_data_send(download_lognum, (1 + highest) * 90)
        retries += 1
    else:
        num_requests = 0
        while num_requests < 20:
            start = min(diff)
            diff.remove(start)
            end = start
            while end + 1 in diff:
                end += 1
                diff.remove(end)
            __log_request_data_send(download_lognum, start * 90, (end + 1 - start) * 90)
            num_requests += 1
            retries += 1
            if len(diff) == 0:
                break


def __log_request_end_send():
    global my_vehicle
    if my_vehicle is not None:
        my_vehicle.message_factory.log_request_end_send(TARGET_SYSTEM, TARGET_COMPONENT)


def __log_request_data_send(log_num, offset=0, number_of_bytes=0xFFFFFFFF):
    global my_vehicle
    if my_vehicle is not None:
        my_vehicle.message_factory.log_request_data_send(0, 0, log_num, offset, number_of_bytes)


def __log_request_list_send(first_log=0, last_log=0xFFFF):
    global my_vehicle
    log_list_lock.acquire()
    if my_vehicle is not None:
        my_vehicle.message_factory.log_request_list_send(TARGET_SYSTEM, TARGET_COMPONENT, first_log, last_log)


def __wait_for_log_list_request_to_finish():
    if log_list_lock.acquire() is False:
        logger.critical("wait_for_request_to_finish , Could not acquire lock")
        return False
    log_list_lock.release()
    return True


def __wait_for_request_to_finish():
    if lock.acquire() is False:
        logger.critical("wait_for_request_to_finish , Could not acquire lock")
        return False
    lock.release()
    return True


def download_all_logs() -> List[str]:
    my_log_list = get_log_list()
    filenames = []
    for my_ap_log in my_log_list:
        filenames.append(log_download(my_ap_log.id))
    return filenames


def __get_log_list():
    global log_entries, num_logs, last_log_num
    log_entries = []
    num_logs = -1
    last_log_num = -1
    __log_request_list_send()
    __wait_for_log_list_request_to_finish()
    return log_entries


def get_log_list():
    global log_entries
    return log_entries


def download_latest_log() -> bool:
    if num_logs > 0:
        log_download(last_log_num)
    return True


def log_download(log_num, progress_callback=default_progress_callback) -> str:
    global download_file, download_lognum, download_filename, download_set, download_start, \
        download_ofs, __progress_callback, retries, download_last_timestamp, is_finished_download
    filename = None
    if log_num <= last_log_num:
        my_future = executor.submit(log_missing_data_task)
        filename = os.path.join(my_log_folder, __default_log_filename(log_num))
        """download a log file"""
        logger.info(f"Downloading log {log_num} as {filename}")
        download_lognum = log_num
        download_file = open(filename, "wb")
        download_filename = filename
        download_set = set()
        download_start = time.time()
        download_last_timestamp = time.time()
        download_ofs = 0
        retries = 0
        is_finished_download = False
        __progress_callback = progress_callback
        __log_request_data_send(log_num)
        lock.acquire(blocking=True)
        __wait_for_request_to_finish()
        is_finished_download = True
        # try:
        #     my_future.result(timeout=2)
        # except TimeoutError:
        #     logger.warning("my future result timeout error")
        download_last_timestamp = None
    else:
        logger.warning(f'Log number {log_num} does not exists')

    return filename


def __default_log_filename(log_num):
    return f"ardupilot_log_{log_num}.bin"


def log_missing_data_task():
    global download_last_timestamp, is_finished_download
    logger.info("Starting handle_log_data_missing")
    '''handle missing log data'''
    while not is_finished_download:
        if download_last_timestamp is not None and time.time() - download_last_timestamp > 0.3:
            download_last_timestamp = time.time()
            handle_log_data_missing()
        time.sleep(0.1)
    logger.info('Idle task finished ')


def erase_all_logs():
    global my_vehicle
    if my_vehicle is not None:
        my_vehicle.message_factory.log_erase_send(0, 0)
