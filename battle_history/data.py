import os.path
import pickle

from util import scrape

from const import battle_history_dir


def download(player_name):
    path = os.path.join(battle_history_dir, player_name)
    if not os.path.isfile(path):
        battles = scrape.battle_history(player_name)
        with open(path, 'wb') as f:
            pickle.dump(battles, f)
    else:
        battles = []
        pass  # TODO: Download only the newest battles & append to file
    return battles


def _load(player_name):
    with open(os.path.join(battle_history_dir, player_name), 'rb') as f:
        return pickle.load(f)


def load(player_name):
    try:
        return _load(player_name)
    except FileNotFoundError:
        download(player_name)
        return _load(player_name)
