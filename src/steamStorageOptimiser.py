import requests
import os
import sys
import vdf
import json
import pandas as pd
from hurry.filesize import size as prettySize
from datetime import timedelta
from cfs import error, warn, ok, note
from colorama import init, Fore, Back, Style
init()


def load_config():
    expected_keys = ["key", "steamid", "install_dir"]

    try:
        with open('config.json') as f:
            config = json.load(f)
        if not all(x in config for x in expected_keys):
            raise json.decoder.JSONDecodeError
        ok("Loaded config file. To change, delete the config file to run setup again, or edit it directly.")
    except FileNotFoundError:
        warn("No config file found.")
        key = input(
            "Enter your API key (create one here: https://steamcommunity.com/dev/apikey (domain is irrelevant)): ")
        steamid = input(
            "Enter your 64-bit SteamID (eg. use this tool https://www.steamidfinder.com/): ")
        config = {"key": key, "steamid": steamid,
                  "install_dir": "C:\Program Files (x86)\Steam\steamapps"}
        with open("config.json", 'w') as f:
            json.dump(config, f)
        ok("Saved new config file.")
        os.system("pause")
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
    except json.decoder.JSONDecodeError as e:
        error(
            f"API response invalid. Expected data, recieved:\n{api_response.text}. \n{Fore.YELLOW}Check your config?{Style.RESET_ALL}{config}")
    return {game["appid"]: game for game in api_response}


def get_library_paths(config):
    try:
        with open(f"{config['install_dir']}\\libraryfolders.vdf") as f:
            libraries = vdf.parse(f)["libraryfolders"]
    except FileNotFoundError as e:
        error(
            f"Problem with libraryfolders file. If Steam not installed at {Fore.YELLOW}{config['install_dir']}{Style.RESET_ALL}, edit your config file and try again.")

    library_paths = []
    for library in libraries.values():
        library_paths.append(library["path"] + "\\steamapps")
    return library_paths


def match_games(config, api_dict):
    games = []
    unmatched_games = []

    for library_path in get_library_paths(config):
        manifests = [f.path for f in os.scandir(
            library_path) if not f.is_dir() and f.name[0] == 'a']
        ok(f"Found {len(manifests)} in library {library_path}.")
        for manifest in manifests:
            try:
                with open(manifest) as f:
                    manifest = vdf.parse(f)
                for game in manifest.values():
                    appid = int(game["appid"])
                    try:
                        api_info = api_dict[appid]
                    except KeyError as e:
                        note(f"Failed to match {appid}: {game['name']}.")
                    else:
                        playtime = api_info["playtime_forever"]
                        size = int(game["SizeOnDisk"])
                        if size != 0:
                            games.append({"name": game["name"],
                                          "bsize": size,
                                          "size": prettySize(size),
                                          "playtime": playtime,
                                          "playtimeH": '{:02d}:{:02d}'.format(*divmod(playtime, 60)),
                                          "timePerByte": playtime/size,
                                          "hoursPerGB": (playtime/60)/(size/1073741824)})
                        else:
                            unmatched_games.append({"name": game["name"],
                                                    "playtime": playtime,
                                                    "playtimeH": '{:02d}:{:02d}'.format(*divmod(playtime, 60))})
            except SyntaxError:
                pass
    return (games, unmatched_games)


def humansize(nbytes):
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
    df.cumulativeSize = df.cumulativeSize.apply(humansize)

    print(
        f"\n{Fore.CYAN + Style.BRIGHT}Found and matched {df.shape[0]} installed games: {Style.RESET_ALL}")
    print(df[["name", "size", "playtimeH", "hoursPerGB",
          "cumulativeSize", "cumulativeTime"]].to_string(index=False))


def output_unmatched(unmatched_games):
    df = pd.DataFrame(unmatched_games)
    df.sort_values("playtime", ascending=False, inplace=True)

    print(
        f"\nFound {df.shape[0]} games not matched (eg. download not complete): ")
    print(df[["name", "playtimeH"]].to_string())


def main():
    config = load_config()
    games, unmatched_games = match_games(config, get_api_response(config))
    output_games(games)
    if len(unmatched_games) > 0:
        output_unmatched(unmatched_games)
    os.system("pause")


if __name__ == '__main__':
    sys.exit(main())
