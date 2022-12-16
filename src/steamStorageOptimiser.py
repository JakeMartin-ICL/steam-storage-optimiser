import json
import os
import platform
import sys
from pathlib import Path

import appdirs
import pandas as pd
import requests
import vdf
from colorama import Fore, Style, init

from cfs import error, note, ok, warn

init()

update_api_threshold = 1024 ** 3
tick = '√' if getattr(
    sys, 'frozen', False) and platform.release() == '10' else '✓'


def load_config():
    expected_keys = ["key", "steamid", "install_dir"]
    config_dir = appdirs.user_config_dir("Steam Storage Optimiser")

    try:
        with open(os.path.join(config_dir, 'config.json')) as f:
            config = json.load(f)
        if not all(x in config for x in expected_keys):
            raise json.decoder.JSONDecodeError
        ok(f"Loaded config file. To change, edit or delete the config file in {config_dir}).")
    except FileNotFoundError:
        warn("No config file found.")
        Path(config_dir).mkdir(parents=True, exist_ok=True)
        if sys.platform == "linux" or sys.platform == "linux2":
            install_dir = os.path.expanduser('~/.steam/steam/steamapps')
        elif sys.platform == "darwin":
            install_dir = os.path.expanduser('~/Library/Application Support/Steam/steamapps')
        else:
            install_dir = 'C:\\Program Files (x86)\\Steam\\steamapps'
        warn(
            f"Setting Steam install location to default. If Steam is not installed at {install_dir}, you can change this in the config file.")
        key = input(
            "Enter your API key (create one here: https://steamcommunity.com/dev/apikey (domain is irrelevant)): ")
        steamid = input(
            "Enter your 64-bit SteamID (eg. use this tool https://www.steamidfinder.com/, it should look like 76561197960287930): ")
        config = {"key": key, "steamid": steamid,
                  "install_dir": install_dir}
        with open(os.path.join(config_dir, 'config.json'), 'w') as f:
            json.dump(config, f)
        ok("Saved new config file.")
        input("Press Enter to continue . . .")
    except json.decoder.JSONDecodeError:
        error("Malformed config file. Delete or fix the config file and try again.")
    return config


def get_api_response(config):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1"
    payload = {'key': config['key'],
               'steamid': config['steamid'], 'include_appinfo': True}

    api_response = requests.get(url, params=payload)
    try:
        api_response = api_response.json()["response"]["games"]
    except json.decoder.JSONDecodeError:
        error(
            f"API response invalid. Expected data, recieved:\n{api_response.text}. \n{Fore.YELLOW}Check your config?{Style.RESET_ALL}{config}")
    return api_response


def get_size_from_api(appid):
    url = f"https://eu5di55p9a.execute-api.eu-west-2.amazonaws.com/default/app/{appid}"
    api_response = requests.get(url)
    if api_response.status_code == requests.codes['not_found']:
        return None
    try:
        api_response = api_response.json()
    except json.decoder.JSONDecodeError:
        error(
            f"API response invalid. Expected data, recieved:\n{api_response.text}. Report this issue on GitHub.")
    return api_response


def get_sizes_from_api(appids):
    url = f"https://eu5di55p9a.execute-api.eu-west-2.amazonaws.com/default/apps"
    sizes = []
    for i in range(0, len(appids), 100):
        id_batch = appids[i:i + 100]
        payload = {'ids': id_batch}

        api_response = requests.get(url, json=payload)

        try:
            api_response = api_response.json()
            sizes += api_response
        except json.decoder.JSONDecodeError:
            error(
                f"API response invalid. Expected data, recieved:\n{api_response.text}. Report this issue on GitHub.")
    return {game['AppId']: game for game in sizes}


def update_api_size(appid, size, name):
    url = f"https://eu5di55p9a.execute-api.eu-west-2.amazonaws.com/default/app/{appid}"
    payload = {'size': size, 'name': name}

    api_response = requests.put(url, params=payload)
    if api_response.status_code != requests.codes['ok']:
        error(f"Error while updating size database. Response: {api_response}")


def add_to_db(appid, size, name):
    url = f"https://eu5di55p9a.execute-api.eu-west-2.amazonaws.com/default/app/{appid}"
    payload = {'size': size, 'name': name}

    api_response = requests.post(url, params=payload)
    if api_response.status_code != requests.codes['ok']:
        error(
            f"Error while adding new game to database. Response: {api_response}")


def get_library_paths(config):
    try:
        with open(os.path.join(config['install_dir'], 'libraryfolders.vdf')) as f:
            libraries = vdf.parse(f)["libraryfolders"]
    except FileNotFoundError:
        error(
            f"Problem finding libraryfolders.vdf file. If SteamApps folder is not located at {Fore.YELLOW}{config['install_dir']}{Style.RESET_ALL}, edit your config file and try again.")

    library_paths = []
    for library in libraries.values():
        if type(library) is dict:
            library_paths.append(os.path.join(library["path"], 'steamapps'))
    return library_paths


def get_installed_games(config):
    installed_games = []

    for library_path in get_library_paths(config):
        try:
            manifests = [f.path for f in os.scandir(
                library_path) if not f.is_dir() and f.name[0] == 'a']
        except OSError:
            warn(f"Library {library_path} missing - skipping.")
            continue
        ok(f"Found {len(manifests)} in library {library_path}.")
        for manifest in manifests:
            try:
                with open(manifest) as f:
                    manifest = vdf.parse(f)
                installed_games += manifest.values()
            except SyntaxError:
                pass

    return {int(game['appid']): game for game in installed_games}


def match_games(owned_games, installed_games):
    games = []
    unmatched_games = []

    db_sizes = get_sizes_from_api([game['appid'] for game in owned_games])
    ok(f"Matched {len(db_sizes)} with database.")

    for game in owned_games:
        appid = game['appid']
        if appid in installed_games:
            installed = True
            size = int(installed_games[appid]['SizeOnDisk'])
            if appid in db_sizes:
                api_size = db_sizes[appid]['Size']
                if abs(api_size - size) > update_api_threshold:
                    ok(f"Updating database. Your install size for {game['name']} is {human_size(size)}. The average size is {human_size(api_size)}")
                    update_api_size(appid, size, game['name'])
            else:
                ok(f"Adding to database. This is the first time {game['name']} has been seen.")
                add_to_db(appid, size, game['name'])
        else:
            installed = False
            size = db_sizes.get(appid)
            if size != None:
                size = size['Size']

        playtime = game["playtime_forever"]
        if size != 0 and size != None:
            games.append({"name": game["name"],
                          "bsize": size,
                          "size": human_size(size),
                          "playtime": playtime,
                          "playtimeH": '{:02d}:{:02d}'.format(*divmod(playtime, 60)),
                          "timePerByte": playtime/size,
                          "hoursPerGB": (playtime/60)/(size/1073741824),
                          "installed": tick if installed else ''})
        else:
            unmatched_games.append({"name": game["name"],
                                    "playtime": playtime,
                                    "playtimeH": '{:02d}:{:02d}'.format(*divmod(playtime, 60))})

    return (games, unmatched_games)


def human_size(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def output_games(games):
    df = pd.DataFrame(games)
    df.sort_values("timePerByte", ascending=False, inplace=True)
    df["cumulativeTime"] = df["playtime"].cumsum()
    df["cumulativeSize"] = df["bsize"].cumsum()
    df.cumulativeTime = df.cumulativeTime.apply(
        lambda x: '{:02d}:{:02d}'.format(*divmod(x, 60)))
    df.cumulativeSize = df.cumulativeSize.apply(human_size)

    note(f"\nFound and matched {df.shape[0]} installed games:")
    print(df[["name", "size", "playtimeH", "hoursPerGB",
          "cumulativeSize", "cumulativeTime", "installed"]].to_string(index=False))


def output_unmatched(unmatched_games):
    df = pd.DataFrame(unmatched_games)
    df.sort_values("playtime", ascending=False, inplace=True)

    note(
        f"\n{df.shape[0]} games not matched. These games are not installed and not yet in the database: ")
    print(df[["name", "playtimeH"]].to_string())


def main():
    config = load_config()
    owned_games = get_api_response(config)
    installed_games = get_installed_games(config)
    games, unmatched_games = match_games(owned_games, installed_games)
    output_games(games)
    if len(unmatched_games) > 0:
        output_unmatched(unmatched_games)
    input("Press Enter to exit . . .")


if __name__ == '__main__':
    sys.exit(main())
