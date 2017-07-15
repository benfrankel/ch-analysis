from util import scrape
from const import battle_history_dir

import os.path
import pickle


def download(player_name):
    path = os.path.join(battle_history_dir, player_name)
    if not os.path.isfile(path):
        battles = scrape.battle_history(player_name)
        with open(path, 'wb') as f:
            pickle.dump(battles, f)
    else:
        pass  # TODO: Download only the newest battles & append to file


def load(player_name):
    with open(os.path.join(battle_history_dir, player_name), 'rb') as f:
        return pickle.load(f)
