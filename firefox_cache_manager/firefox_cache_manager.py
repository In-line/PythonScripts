#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path

"""Should be used with profile-sync-daemon"""
"""Seems to be somewhat complicated, but I didn't find other clear method to do it"""


def main():
    backup_profile_regex = re.compile("^.+?-(back|backup).+?$")
    profile_regex = re.compile("^([a-z]+?)\.default.*?$")

    profile_root_path = Path(os.environ["HOME"], '.mozilla', 'firefox')
    cache_root_path = Path(os.environ["HOME"], '.cache', 'mozilla', 'firefox')

    profile_dirs = filter(lambda x: x.is_dir() and profile_regex.match(x.name), profile_root_path.iterdir())
    for profile in profile_dirs:
        cache_path = Path(cache_root_path, profile.name)
        cache_in_profile_path_root = Path(profile, 'cache')
        cache_in_profile_path = Path(cache_in_profile_path_root, profile.name)

        if not cache_in_profile_path_root.exists():
            cache_in_profile_path_root.mkdir()

        if backup_profile_regex.match(profile.as_posix()):
            clear_cache_in_profile(cache_in_profile_path_root)
        elif cache_path.exists() and cache_in_profile_path.exists() and \
                cache_path.resolve() == cache_in_profile_path.resolve():
            continue
        else:
            if cache_path.is_dir():
                shutil.move(cache_path, cache_in_profile_path)
            else:
                universal_remove(cache_path)
                universal_remove(cache_in_profile_path)

                cache_in_profile_path.mkdir()
                cache_path.symlink_to(cache_in_profile_path, True)
            print("Created symlink ", cache_path, " -> ", cache_in_profile_path)


def clear_cache_in_profile(cache_full_path):
    if cache_full_path.exists():
        paths_to_delete = list(cache_full_path.iterdir())
        for one_path in paths_to_delete:
            try:
                shutil.rmtree(str(one_path))
            except NotADirectoryError:
                one_path.unlink()
        if paths_to_delete:
            print("Cache cleared in profile: ", cache_full_path)


def universal_remove(full_path):
    if full_path.is_dir():
        shutil.rmtree(full_path, ignore_errors=True)
    elif full_path.is_symlink() or full_path.is_file():
        full_path.unlink()


main()
