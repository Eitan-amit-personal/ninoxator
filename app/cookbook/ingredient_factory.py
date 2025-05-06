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
from app.cookbook.ingredient_local_docker import IngredientLocalDocker
from app.cookbook.ingredient_local_file import IngredientLocalFile
from app.cookbook.ingredient_transport import IngredientTransport
from app.cookbook.ingredient_github import IngredientGitHub
from app.cookbook.ingredient_http import IngredientHttp
from app.cookbook.ingredient_docker import IngredientDocker
from app.cookbook.ingredient_script import IngredientScript


def ingredient_factory(ingredient: dict) -> IngredientTransport:
    if ingredient['source_type'] == 'http':
        return IngredientHttp(ingredient)

    if ingredient['source_type'] == 'github':
        return IngredientGitHub(ingredient)

    if ingredient['source_type'] == 'docker':
        return IngredientDocker(ingredient)

    if ingredient['source_type'] == 'script':
        return IngredientScript(ingredient)

    if ingredient['source_type'] == 'localfile':
        return IngredientLocalFile(ingredient)

    if ingredient['source_type'] == 'localdocker':
        return IngredientLocalDocker(ingredient)
