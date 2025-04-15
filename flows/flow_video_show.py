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
import subprocess


def drone_video_show() -> bool:
    cmd = ['gst-launch-1.0',
           'udpsrc',
           'port=5600',
           'caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264"',
           '!',
           'rtph264depay',
           '!',
           'avdec_h264',
           '!',
           'videoconvert',
           '!',
           'autovideosink']
    try:
        p = subprocess.Popen(cmd)
        p.communicate()
    except Exception:
        pass

    return True


if __name__ == "__main__":
    drone_video_show()
