#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2021
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
import tarfile
import tempfile

from ninox_common.git_wrapper import download_release_assets, get_latest_release_name
from app.cookbook.cookbook import CookBook

COOKBOOK_REPO = 'spearuav/ninoxator-cookbook'
ASSETS_FOLDER = 'data'


def test_cookbook_class():
    meal = get_meal()
    b = CookBook(meal)
    print(f'meal type {b.meal_type}')
    print(f'meal version {b.meal_version}')
    print(f'meal flavour {b.meal_flavor}')
    print(f'device type {b.device_type}')
    print(b.recipe)


def test_cookbook_fetch_files():
    meal = get_meal()
    b = CookBook(meal)
    print(b.recipe.fetch_files(ASSETS_FOLDER))


def test_fetch_lua_script():
    data = get_meal('viper300-1.9-2.5.1.json')     # first version with working lua script
    b = CookBook(data)
    print(b.recipe.fetch_files(ASSETS_FOLDER))


def get_meal(sample_file='viper300-0.0-0.0.json'):
    latest_release_name = get_latest_release_name(COOKBOOK_REPO)
    print(f'Latest cookbook release {latest_release_name}')

    cookbook_tar_name = download_release_assets(COOKBOOK_REPO, latest_release_name, ASSETS_FOLDER,
                                                asset_name='cookbooks.tar.gz', optimize_download=False)[0]
    with tarfile.open(f'{ASSETS_FOLDER}/{cookbook_tar_name}', 'r') as cookbook_tar:
        with tempfile.TemporaryDirectory() as temp_dir:
            cookbook_tar.extract(sample_file, path=temp_dir)
            extracted_file_path = os.path.join(temp_dir, sample_file)
            with open(extracted_file_path) as file:
                data = file.read()

    return data


def test_get_latest_meal():
    data = get_meal()
    assert data is not None
