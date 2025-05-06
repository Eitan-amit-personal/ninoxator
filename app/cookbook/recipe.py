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
from halo import Halo
from ninox_common.log import Loggable
from prettytable import PrettyTable

from app.cookbook.ingredient_transport import IngredientTransport
from app.cookbook.ingredient_factory import ingredient_factory


class Recipe(Loggable):
    def __init__(self, recipe: dict):
        super().__init__()
        self.ingredients: list[IngredientTransport] = []
        self.__add_recipe(recipe)

    def __add_recipe(self, recipe):
        for ingredient in recipe:
            self.ingredients.append(ingredient_factory(ingredient))

    def fetch_files(self, dest_dir: str, progress_callback=None) -> list:
        files_list = []
        for ingredient in self.ingredients:
            self.logger.info(f'Fetch {ingredient.name} {ingredient.version}')
            with Halo(text=f'Fetch {ingredient.name} {ingredient.version}', spinner='bouncingBar') as spinner:
                file_name = (ingredient.fetch_files(dest_dir))
                self.logger.info(f"File name from fetch: {file_name}")
                if file_name is not None:
                    spinner.succeed(f"downloaded {ingredient.name} {ingredient.version}")
                else:
                    spinner.fail(f"download {ingredient.name} failed ")
                files_list.append(file_name)

            if progress_callback:
                progress_callback()
        return files_list

    def get_ingredient(self, name: str):
        for ingredient in self.ingredients:
            if ingredient.name == name:
                return ingredient
        return None

    def get_ingredient_list(self) -> list:
        return self.ingredients

    def __str__(self):
        x = PrettyTable()
        x.field_names = ["name", "version", "source_type"]
        for ingredient in self.ingredients:
            if ingredient:
                x.add_row([ingredient.name, ingredient.version, ingredient.source_type])
        x.align = "l"
        return f'{x}'
