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

import json
from typing import Optional
from json import JSONDecodeError

from app.cookbook.recipe import Recipe


class CookBook:
    def __init__(self, cookbook_json_str: str):
        self._device_type: str = ""
        self._meal_type: str = ""
        self._meal_flavor: str = ""
        self._meal_version: str = ""
        self.recipe: Optional[Recipe] = None
        self._parse_json(cookbook_json_str)

    def _parse_json(self, cookbook_json_str):
        try:
            json_obj = json.loads(cookbook_json_str)
            self._device_type = json_obj['device_type']
            self._meal_type = json_obj['meal_type']
            self._meal_flavor = json_obj['meal_flavor']
            self._meal_version = json_obj['meal_version']
            self.recipe = Recipe(json_obj['recipe'])
        except JSONDecodeError:
            pass
        except TypeError:
            pass

    @property
    def device_type(self):
        return self._device_type

    @property
    def meal_type(self):
        return self._meal_type

    @property
    def meal_version(self):
        return self._meal_version

    @property
    def meal_flavor(self):
        return self._meal_flavor
