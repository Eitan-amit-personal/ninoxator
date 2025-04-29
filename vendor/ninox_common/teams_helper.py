#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
# __author__ = "Daniel Weingut"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################

import pymsteams
import base64
from ninox_common.api_tokens import TEAMS_URL, TEAMS_SOFTWARE_CHANNEL

notifier = pymsteams.connectorcard(TEAMS_URL)
my_teams_message = pymsteams.connectorcard(TEAMS_SOFTWARE_CHANNEL)


def send_via_notifier(text: str) -> bool:
    notifier.text(text)
    result = notifier.send()
    return result


def make_section_text(text: str):
    my_message_section = pymsteams.cardsection()
    my_message_section.text(text)
    return my_message_section


def make_section_image(title: str, activity_text: str, image_url: str):
    my_message_section = pymsteams.cardsection()
    my_message_section.title(title)
    my_message_section.activityImage(image_url)
    my_message_section.text(activity_text)
    return my_message_section


def make_section_local_image(title: str, activity_text: str, image_path: str):  # only from the local memory
    try:
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode('ascii')
            data_uri = "data:image/jpeg;base64, " + encoded
            return make_section_image(title, activity_text, data_uri)
    except Exception:
        return None


def make_section_link_button(link_button: str, text_button: str):
    my_message_section = pymsteams.cardsection()
    my_message_section.linkButton(text_button, link_button)
    return my_message_section


def send_sections_to_spear_software_channel(*sections):
    for section in sections:
        my_teams_message.addSection(section)
    my_teams_message.summary(".")
    my_teams_message.send()
