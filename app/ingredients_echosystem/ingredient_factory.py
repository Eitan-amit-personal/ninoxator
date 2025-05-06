#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2023
# All rights reserved.
#
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
from typing import Union
from ninox_common.log import Loggable

from app.drone import Drone
from app.cookbook.ingredient_transport import IngredientTransport
from app.ingredients_echosystem.ingredients.ardupilot_firmware_ingredient import ArdupilotFirmwareIngredient
from app.ingredients_echosystem.ingredients.ardupilot_parameters_ingredient import ArdupilotParametersIngredient
from app.ingredients_echosystem.ingredients.c2_ingredient import C2Ingredient
from app.ingredients_echosystem.ingredients.cc_ingredient import CCIngredient
from app.ingredients_echosystem.ingredients.docker_deploy_ingredient_local import DockerDeployLocalIngredient
from app.ingredients_echosystem.ingredients.ingredient import Ingredient
from app.ingredients_echosystem.ingredients.mavproxy_ingredient import MAVProxyIngredient
from app.ingredients_echosystem.ingredients.telemetry_ingredient import TelemetryIngredient
from app.ingredients_echosystem.ingredients.mcu_attack_ingredient import McuAttackIngredient
from app.ingredients_echosystem.ingredients.mcu_gimbal_ingredient import McuGimbalIngredient
from app.ingredients_echosystem.ingredients.null_ingredient import NullIngredient
from app.ingredients_echosystem.ingredients.remote_ardupilot_firmware_ingredient import \
    RemoteArdupilotFirmwareIngredient
from app.ingredients_echosystem.ingredients.ui_flask_ingredient import UiFlaskIngredient
from app.ingredients_echosystem.ingredients.ui_flutter_ingredient import UiFlutterIngredient
from app.ingredients_echosystem.ingredients.vision_computer_ingredient import VisionComputerIngredient
from app.ingredients_echosystem.ingredients.vision_computer_calibration_ingredient import \
    VisionComputerCalibrationIngredient
from app.ingredients_echosystem.ingredients.vision_computer_pyinstaller_ingredient import \
    VisionComputerPyinstallerIngredient
from app.ingredients_echosystem.ingredients.vision_computer_flask_pyinstaller_ingredient import \
    VisionComputerFlaskPyinstallerIngredient
from app.ingredients_echosystem.ingredients.companion_computer_flask_pyinstaller_ingredient import \
    CompanionComputerFlaskPyinstallerIngredient
from app.ingredients_echosystem.ingredients.docker_deploy_ingredient import DockerDeployIngredient
from app.ingredients_echosystem.ingredients.clean_services_ingredient import CleanServicesIngredient
from app.ingredients_echosystem.ingredients.ap_script_ingredient import ArdupilotLuaScriptIngredient
from app.ingredients_echosystem.ingredients.companion_computer_parameters_ingredient import \
    CompanionComputerParametersIngredient
from app.ingredients_echosystem.ingredients.vision_computer_parameters_ingredient import \
    VisionComputerParametersIngredient


class IngredientFactory(Loggable):
    def __init__(self):
        super().__init__()

    @staticmethod
    def name_to_ingredient(drone: Drone, ingredient: IngredientTransport, drone_id: int) -> Union[Ingredient, list]:
        if ingredient.name == 'ardupilot-firmware':
            return ArdupilotFirmwareIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name == 'remote-ardupilot-firmware':
            return RemoteArdupilotFirmwareIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name == 'ardupilot-parameters':
            return ArdupilotParametersIngredient(ingredient.local_file_path, drone=drone, drone_id=drone_id)
        elif ingredient.name == 'microhard-firmware':
            return NullIngredient(ingredient.local_file_path, drone=drone)
        #            return MicrohardFirmwareIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name == 'microhard-parameters':
            return NullIngredient(ingredient.local_file_path, drone=drone)
        #            return MicrohardParametersIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name == 'cc':
            return CCIngredient(ingredient.local_file_path, ingredient.version, drone=drone)
        elif ingredient.name == 'drone-ui-flask':
            return UiFlaskIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name in 'drone-ui-flutter':
            return UiFlutterIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name in 'mcu-attack':
            return McuAttackIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name in 'mcu-gimbal':
            return McuGimbalIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name in 'vision-computer':
            return VisionComputerIngredient(ingredient.local_file_path, ingredient.version, drone=drone)
        elif ingredient.name in 'vision-computer-pyinstaller':
            return VisionComputerPyinstallerIngredient(ingredient.local_file_path, ingredient.version, drone=drone)
        elif ingredient.name in 'vision-computer-flask-pyinstaller':
            return VisionComputerFlaskPyinstallerIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name in 'vision-computer-flask-docker':
            return [DockerDeployIngredient(ingredient.local_file_path,
                                           ingredient.version,
                                           drone=drone,
                                           run_cmd=ingredient.run_cmd),
                    CleanServicesIngredient(ingredient.local_file_path, drone=drone)]
        elif ingredient.name in 'vision-computer-flask-docker-local':
            return [DockerDeployLocalIngredient(ingredient.local_file_path,
                                                ingredient.container,
                                                ingredient.version,
                                                drone=drone,
                                                run_cmd=ingredient.run_cmd),
                    CleanServicesIngredient(ingredient.local_file_path, drone=drone)]
        if ingredient.name == 'companion-computer-flask-pyinstaller':
            return CompanionComputerFlaskPyinstallerIngredient(ingredient.local_file_path, run_cmd=ingredient.run_cmd,
                                                               drone=drone)
        elif ingredient.name == 'vision-computer-docker':
            return DockerDeployIngredient(ingredient.local_file_path,
                                          ingredient.version,
                                          drone=drone,
                                          run_cmd=ingredient.run_cmd)
        elif ingredient.name == 'vision-computer-docker-local':
            return DockerDeployLocalIngredient(ingredient.local_file_path,
                                               ingredient.container,
                                               ingredient.version,
                                               drone=drone,
                                               run_cmd=ingredient.run_cmd)
        elif ingredient.name == 'vision-computer-calibration':
            return VisionComputerCalibrationIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name == 'navigation-computer-docker':
            return DockerDeployIngredient(ingredient.local_file_path,
                                          ingredient.version,
                                          drone=drone,
                                          run_cmd=ingredient.run_cmd)
        elif ingredient.name == 'navigation-computer-docker-local':
            return DockerDeployLocalIngredient(ingredient.local_file_path,
                                               ingredient.container,
                                               ingredient.version,
                                               drone=drone,
                                               run_cmd=ingredient.run_cmd)
        elif ingredient.name == 'lua-script':
            return ArdupilotLuaScriptIngredient(ingredient.local_file_path, ingredient.version, drone=drone)
        elif ingredient.name == 'cc-parameters':
            return CompanionComputerParametersIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name == 'vc-parameters':
            return VisionComputerParametersIngredient(ingredient.local_file_path, drone=drone)
        elif ingredient.name == 'mavproxy-service':
            return MAVProxyIngredient(drone=drone, run_cmd=ingredient.run_cmd)
        elif ingredient.name == 'telemetry-service':
            return TelemetryIngredient(ingredient.local_file_path, run_cmd=ingredient.run_cmd, drone=drone)
        elif ingredient.name == 'c2':
            return C2Ingredient(drone=drone, source_file_path=ingredient.local_file_path)
        else:
            print(f"ingredient '{ingredient.name}' is not implemented, skipping...")
            return NullIngredient(ingredient.local_file_path, drone=drone)
