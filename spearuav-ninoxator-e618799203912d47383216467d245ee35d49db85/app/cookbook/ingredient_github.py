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
from ninox_common.git_wrapper import download_release_assets

from app.cookbook.ingredient_transport import IngredientTransport


class IngredientGitHub(IngredientTransport):
    def __init__(self, ingredient: dict):
        self._tag: str = ''
        self._repo: str = ''
        super().__init__(ingredient)
        self.ingredient_parse_json(ingredient)

    def ingredient_parse_json(self, recipe_json: dict):
        super().ingredient_parse_json(recipe_json)
        json_object = recipe_json
        if 'file_name' in json_object:
            self._filename = json_object['file_name']

        if 'repo' in json_object:
            self._repo = json_object['repo']

        if 'tag' in json_object:
            self._tag = json_object['tag']

        if 'release' in json_object:
            self._tag = json_object['release']

        if 'version' in json_object:
            self._version = json_object['version']
        else:
            self._version = self._tag

        if 'run_cmd' in json_object:
            self._run_cmd = json_object['run_cmd']

    def fetch_files(self, dest_dir: str):
        file_list = []
        local_file_path = f'{dest_dir}/{self.filename}'
        self.logger.info(f'Fetching {self.filename} version {self.tag} from {self.repo}')
        file_list = download_release_assets(self.repo, self.tag, dest_dir, asset_name=self.filename,
                                            optimize_download=True)
        self._local_file_path = local_file_path
        return file_list

    @property
    def tag(self):
        return self._tag

    @property
    def repo(self):
        return self._repo

    @property
    def filename(self):
        return self._filename
