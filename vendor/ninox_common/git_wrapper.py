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
import zipfile
from pathlib import Path

import requests
from github import Github
from github.GitRelease import GitRelease

from ninox_common.vault_service import get_secret

COMPANION_REPO = 'spearuav/ninox-companion'

__github_single_instance = None


def get_release_list(repo_name) -> list:
    release_list: list = []
    releases = __get_releases(repo_name)
    for release in releases:
        release_list.append(release.tag_name)

    return release_list


def download_release_assets(repo_name: str,
                            release_tag: str,
                            destination_folder: str,
                            asset_name: str = '',
                            optimize_download: bool = True,
                            file_extensions: list = []) -> list:

    """
    Downloads release assets from a given GitHub repository and release tag.

     Parameters:
    - repo_name: GitHub repository name # in the format 'owner/repo'.
    - release_tag: The tag of the release to download assets from.
    - destination_folder: The local folder to download the assets to.
    - asset_name: The name of the file we want to download.
    - optimize_download: If True, skips downloading files that already exist and match size.
    - file_extensions: List of file extensions to download (e.g. ['yaml', 'json']).

    """
    release = __get_release(repo_name, release_tag)
    asset_list = []

    if not os.path.exists(destination_folder):
        Path(destination_folder).mkdir(exist_ok=True, parents=True)

    # Determine if asset_name is a wildcard pattern (e.g. "*.yaml")
    if asset_name.startswith('*.'):
        wildcard_extension = asset_name.split('*.')[-1]  # Extract the extension, e.g., 'yaml'
        file_extensions.append(wildcard_extension)

    for asset in release.raw_data['assets']:
        if asset_name and asset['name'] == asset_name:
            # Match the asset name exactly
            pass
        elif file_extensions and any(asset['name'].endswith(f".{ext}") for ext in file_extensions):
            # Match based on the extensions
            pass
        else:
            # Skip assets that match neither the name nor the extensions
            continue

        file_full_path = f"{destination_folder}/{asset['name']}"
        needs_download = True

        if optimize_download and os.path.isfile(file_full_path) and asset['size'] == Path(file_full_path).stat().st_size:
            needs_download = False

        if needs_download:
            if os.path.isfile(file_full_path):
                os.remove(file_full_path)
            github_token = get_secret('github-token')
            r = requests.get(asset['url'], headers={'Authorization': f'token {github_token["password"]}',
                                                    'Accept': 'application/octet-stream'})
            with open(file_full_path, 'wb') as f:
                f.write(r.content)
            asset_list.append(asset['name'])

    return asset_list


def get_latest_release_name(repo_name) -> str:
    repo = __get_instance().get_repo(repo_name)
    return repo.get_latest_release().tag_name


def get_release_assets(repo_name: str, release_tag: str) -> list:
    release = __get_release(repo_name, release_tag)
    asset_list = []
    for asset in release.raw_data['assets']:
        asset_list.append(asset['name'])

    return asset_list


def get_latest_release_assets(repo_name: str) -> list:
    return get_release_assets(repo_name, get_latest_release_name(repo_name))


def get_companion_latest_release_name() -> str:
    return get_latest_release_name(COMPANION_REPO)


def get_file_content(repo_name: str, file_path: str, ref="main"):
    """
    :param repo_name:
    :param file_path:
    :param ref:
    :return:
    """
    repo = __get_instance().get_repo(repo_name)
    file = repo.get_contents(file_path, ref=ref)
    return file.decoded_content.decode("utf-8")


def get_tags(repo_name: str):
    """
    :param repo_name:
    :return:
    """
    repo = __get_instance().get_repo(repo_name)
    tags = repo.get_tags()
    tags_list = []
    for tag in tags:
        tags_list.append(tag.name)
    return tags_list


def download_tag_repo(repo_name: str, tag: str, download_location: str) -> str:
    """
    :param repo_name:
    :param tag:
    :param download_location:
    :return: extract_location
    :rtype: str
    """
    extract_location = f"{download_location}/{tag}"
    if os.path.exists(extract_location):
        return extract_location

    release = __get_release(repo_name, tag)

    github_token = get_secret('github-token')
    r = requests.get(release.zipball_url, headers={'Authorization': f'token {github_token["password"]}'})
    Path(download_location).mkdir(exist_ok=True, parents=True)
    zip_path = f"{download_location}/{tag}.zip"
    open(zip_path, 'wb').write(r.content)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_location)
        return extract_location


def __get_instance() -> Github:
    global __github_single_instance
    if __github_single_instance is None:
        github_token = get_secret('github-token')
        __github_single_instance = Github(github_token['password'])

    return __github_single_instance


def __get_releases(repo_name):
    repo = __get_instance().get_repo(repo_name)
    return repo.get_releases()


def __get_release(repo_name: str, tag_name: str) -> GitRelease:
    repo = __get_instance().get_repo(repo_name)
    return repo.get_release(tag_name)


def get_ninox_drone_configuration_file(file_path):
    return get_file_content('spearuav/ninox-drone-configuration-files', file_path, ref='master')
