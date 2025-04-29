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
import os
from urllib.parse import urlparse

import requests

from app.cookbook.ingredient_transport import IngredientTransport


class IngredientHttp(IngredientTransport):
    def __init__(self, ingredient: dict):
        self._url: str = ''
        super().__init__(ingredient)

    def ingredient_parse_json(self, recipe_json: dict):
        super().ingredient_parse_json(recipe_json)
        json_object = recipe_json
        self._url = json_object['url']
        self._filename = os.path.basename(urlparse(self.url).path)
        if 'version' in json_object:
            self._version = json_object['version']

    def fetch_files(self, dest_dir: str) -> list:
        file_list = []
        full_path = f'{dest_dir}/{self.filename}'
        if not os.path.exists(full_path):
            self.logger.info(f'Fetching {self.filename} from {self.url}')
            r = requests.get(self.url)
            with open(full_path, 'wb') as f:
                f.write(r.content)
            file_list = self.filename
        else:
            self.logger.debug(f'File {self.filename} exists , skipping')

        self._local_file_path = full_path

        return file_list

    @property
    def url(self):
        return self._url

    @property
    def filename(self):
        return self._filename
