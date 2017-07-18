from util import scrape

from const import battles_dir

import os.path
import pickle
from collections import defaultdict


players = {}


# Flags
is_loaded = defaultdict(bool)


def download(player_name):
    if not os.path.exists(battles_dir):
        os.makedirs(battles_dir)

    path = os.path.join(battles_dir, player_name)
    if not os.path.isfile(path):
        battles = scrape.battles(player_name)
        with open(path, 'wb') as f:
            pickle.dump(battles, f)
    else:
        battles = []
        pass  # TODO: Download only the newest battles & append to file
    return battles


def _load(player_name):
    global is_loaded
    if not is_loaded[player_name]:
        with open(os.path.join(battles_dir, player_name), 'rb') as f:
            players[player_name] = pickle.load(f)
        is_loaded[player_name] = True
    return players[player_name]


def load(player_name):
    try:
        return _load(player_name)
    except FileNotFoundError:
        download(player_name)
        return _load(player_name)
