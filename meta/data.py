from util import scrape

from const import BATTLES_DIR

import os.path
import pickle
from collections import defaultdict


battles = []


# Flags
is_loaded = False


def download():
    global battles

    if not os.path.exists(BATTLES_DIR):
        os.makedirs(BATTLES_DIR)

    path = os.path.join(BATTLES_DIR, '.all')
    if not os.path.isfile(path):
        battles = scrape.all_battles()
        with open(path, 'wb') as f:
            pickle.dump(battles, f)
    else:
        battles = []
        pass  # TODO: Download only the newest meta & append to file
    return battles


def load():
    global is_loaded, battles
    with open(os.path.join(BATTLES_DIR, '.all'), 'rb') as f:
        battles = pickle.load(f)
    is_loaded = True


def load_player(player_name):
    if not is_loaded:
        load()
    return filter(lambda x: x['winner'][0] == player_name or x['loser'][0] == player_name, battles)


def load_guild(guild_name):
    if not is_loaded:
        load()
    return filter(lambda x: x['winner'][1] == guild_name or x['loser'][1] == guild_name, battles)
