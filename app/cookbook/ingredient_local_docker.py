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

from app.cookbook.ingredient_transport import IngredientTransport
from app.helpers.hash_helper import hash_file


class IngredientLocalDocker(IngredientTransport):
    def __init__(self, ingredient: dict):
        super().__init__(ingredient)

    def ingredient_parse_json(self, recipe_json: dict):
        super().ingredient_parse_json(recipe_json)
        json_object = recipe_json
        self._container = json_object['container']
        self._filename = self.container.rsplit("/")[-1] + "-docker.tar.gz"
        if 'run_cmd' in json_object:
            self._run_cmd = json_object['run_cmd']
        if 'version' in json_object:
            self._version = json_object['version']

    def fetch_files(self, dest_dir: str) -> list:
        # validate docker image checksum
        _ret = None
        try:
            with open(f"{dest_dir}/file_hashes.txt", "r") as file:
                data = file.read().replace("\n", " ")
                hashes = data.split(" ")
                correct_file_hash = ''
                self.logger.info(f"Docker validate image  {dest_dir}/{self._filename}")
                for index, element in enumerate(hashes):
                    if self._filename in element:
                        correct_file_hash = hashes[index + 1]
                        break
                self.logger.info(f"Correct file hash: {correct_file_hash}")
                local_file_hash = hash_file(f"{dest_dir}/{self._filename}")
                self.logger.info("Local file hash")
                if local_file_hash == correct_file_hash:
                    print(f"Validated docker image {self._filename}")
                    self._local_file_path = f"{dest_dir}/{self._filename}"
                    _ret = [self._filename]
        except Exception as e:
            self.logger.error(f"Error occured: {e}")
        return _ret
