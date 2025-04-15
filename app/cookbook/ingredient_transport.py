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
from ninox_common.log import Loggable


class IngredientTransport(Loggable):
    def __init__(self, ingredient: dict):
        super().__init__()
        self._container = ''
        self._name: str = ''
        self._source_type: str = ''
        self._version: str = ''
        self._filename: str = ''
        self._force_update: bool = False
        self._run_cmd = ''
        self.ingredient_parse_json(ingredient)
        self._local_file_path: str = ''

    def ingredient_parse_json(self, recipe_json: dict):
        try:
            self._name = recipe_json['ingredient_name']
            self._source_type = recipe_json['source_type']
        except KeyError:
            self.logger.error(f'{self._name} KeyError')

        if 'force_cook' in recipe_json:
            self._force_update = recipe_json['force_cook'] is True

    def fetch_files(self, dest_dir: str) -> list:
        pass

    @property
    def name(self):
        return self._name

    @property
    def source_type(self):
        return self._source_type

    @property
    def version(self):
        return self._version

    @property
    def force_update(self):
        return self._force_update

    @property
    def local_file_path(self):
        return self._local_file_path

    @property
    def run_cmd(self):
        return self._run_cmd

    @property
    def container(self):
        return self._container
