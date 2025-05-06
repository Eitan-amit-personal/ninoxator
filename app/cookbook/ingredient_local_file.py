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
import glob
import os.path

from app.helpers.hash_helper import hash_file
from app.cookbook.ingredient_transport import IngredientTransport


class IngredientLocalFile(IngredientTransport):
    def __init__(self, ingredient: dict):
        super().__init__(ingredient)

    def ingredient_parse_json(self, recipe_json: dict):
        super().ingredient_parse_json(recipe_json)
        json_object = recipe_json
        if "url" in json_object:
            self._filename = json_object["url"].split("/")[-1]  # end of url is filename
        else:
            self._filename = json_object["file_name"]
        if 'version' in json_object:
            self._version = json_object['version']
        if 'run_cmd' in json_object:
            self._run_cmd = json_object['run_cmd']

    def fetch_files(self, dest_dir: str) -> list:
        # validate checksum
        _ret = []
        try:
            with open(f"{dest_dir}/file_hashes.txt", "r") as file:
                data = file.read()
                hashes = data.replace("\n", " ").split(" ")
                self.logger.info(f"Validate local file {dest_dir}/{self._filename}")
                files_list = glob.glob(os.path.join(dest_dir, self._filename))
                for current_file in files_list:
                    correct_file_hash = ''
                    for index, element in enumerate(hashes):
                        if os.path.basename(current_file) in element:
                            correct_file_hash = hashes[index + 1]
                            break
                    self.logger.info(f"Correct file hash: {correct_file_hash}")
                    local_file_hash = hash_file(current_file)
                    self.logger.info(f"Local file hash: {local_file_hash}")
                    if local_file_hash == correct_file_hash:
                        print(f"Validated {current_file}")
                        self._local_file_path = f"{current_file}"
                        _ret.append(current_file)
        except Exception as e:
            self.logger.error(f"Error occurred: {e}")
        return _ret
