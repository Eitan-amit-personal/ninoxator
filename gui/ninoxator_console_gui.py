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
from colors import color
from consolemenu import MenuFormatBuilder, ConsoleMenu
from consolemenu.items import FunctionItem
from consolemenu.menu_component import Dimension

import flows.flow_verify_viper_hardware_connectivity
from app.helpers.cli_helper import SPEAR_LOGO
from app.helpers.debug_helper import verbose_mode, toggle_verbose_mode
from flows.flow_cookbook_update import main as flow_cookbook_update
from flows.flow_flash_blank_nanopi import flash_blank_nanopi_flow
from flows.flow_cookbook_update_local import main as drone_local_cookbook_complete_update_flow
from flows.flow_reset_drone_version import flash_reset_drone_version_flow
from flows.flow_set_drone_id import drone_set_drone_id_flow
from flows.flow_video_show import drone_video_show
from flows.flow_drone_dockers_clear import drone_dockers_clear
from flows.flow_dual_teensy_reset import dual_teensy_reset
from flows.flow_control_telemetry_service import control_telemetry_service_flow
from flows.flow_upload_logs import upload_logs_flow
from version import get_version


thin = Dimension(width=100, height=40)  # Use a Dimension to limit the "screen width" to 100 characters
menu_format = MenuFormatBuilder(max_dimension=thin)
menu_format.set_prologue_text_align('center')  # Center the prologue text (by default it's left-aligned)
menu_format.show_prologue_bottom_border(True)  # Show a border under the prologue

menu = ConsoleMenu(f'{SPEAR_LOGO}Ninoxator - {get_version()}')
menu.formatter = menu_format


def get_verbose_text():
    return f"Toggle verbose mode - [{color('TRUE' if verbose_mode() else 'FALSE', 'green' if verbose_mode() else 'default')}]"


# A FunctionItem runs a Python function when selected
function_item1 = FunctionItem("Cookbook drone update", flow_cookbook_update)
function_item2 = FunctionItem("Cookbook local version update!", drone_local_cookbook_complete_update_flow, [False])
function_item3 = FunctionItem("Reset drone software version", flash_reset_drone_version_flow)
function_item4 = FunctionItem("Flash new Nanopi", flash_blank_nanopi_flow)
function_item5 = FunctionItem("Set drone ID", drone_set_drone_id_flow)
function_item6 = FunctionItem("Clear dockers from drone!", drone_dockers_clear)
function_item7 = FunctionItem("Check Viper HW connectivity", flows.flow_verify_viper_hardware_connectivity.main)
function_item8 = FunctionItem("Test drone video", drone_video_show)
function_item9 = FunctionItem("Cookbook simulator update!", flow_cookbook_update, [False])
function_item10 = FunctionItem("Dual-Teensy initial burn (reset)", dual_teensy_reset)
function_item11 = FunctionItem("Stop TELEMETRY service", control_telemetry_service_flow, [False])
function_item12 = FunctionItem("Start TELEMETRY service", control_telemetry_service_flow, [True])
function_item13 = FunctionItem("Upload logs (NanoPi, Jetson)", upload_logs_flow)
function_item14 = FunctionItem(get_verbose_text, toggle_verbose_mode)

# Once we're done creating them, we just add the items to the menu

menu.append_item(function_item1)
menu.append_item(function_item2)
menu.append_item(function_item3)
menu.append_item(function_item4)
menu.append_item(function_item5)
menu.append_item(function_item6)
menu.append_item(function_item7)
menu.append_item(function_item8)
menu.append_item(function_item9)
menu.append_item(function_item10)
menu.append_item(function_item11)
menu.append_item(function_item12)
menu.append_item(function_item13)
menu.append_item(function_item14)


# Finally, we call show to show the menu and allow the user to interact

try:
    menu.show()
except KeyboardInterrupt:
    exit(0)
