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

from app.cookbook.ingredient_transport import IngredientTransport


class IngredientDocker(IngredientTransport):
    def __init__(self, ingredient: dict):
        self._container = ""
        super().__init__(ingredient)

    def ingredient_parse_json(self, recipe_json: dict):
        super().ingredient_parse_json(recipe_json)
        json_object = recipe_json
        self._container = json_object['container']
        if 'run_cmd' in json_object:
            self._run_cmd = json_object['run_cmd']
        if 'version' in json_object:
            self._version = json_object['version']

    def fetch_files(self, dest_dir: str) -> list:
        self._local_file_path = self.container
        # docker ingredient does not fetch files
        return []
