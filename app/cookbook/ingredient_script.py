#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2024
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


class IngredientScript(IngredientTransport):
    def __init__(self, ingredient: dict):
        super().__init__(ingredient)

    def ingredient_parse_json(self, recipe_json: dict):
        super().ingredient_parse_json(recipe_json)
        json_object = recipe_json
        if 'run_cmd' in json_object:
            self._run_cmd = json_object['run_cmd']

    def fetch_files(self, dest_dir: str) -> list:
        # script ingredient has no files to fetch
        return []
