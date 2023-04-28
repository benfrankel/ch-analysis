import datetime
import os

import aiohttp

import cache
from . import api
from . import model


_MIN_BATTLE_ID = 3_086_851

_GAME_TYPES = (
    'CASUAL',
    'CUSTOM',
    'LEAGUE',
    'RANKED',
)
_GAME_TYPE_TO_IDX = {
    'CASUAL': 0,
    'CUSTOM': 1,
    'LEAGUE': 2,
    'RANKED': 3,
}

# Local cache paths
BASE_DIRPATH = os.path.join(cache.BASE_DIRPATH, 'metadata')

PLAYER_NAMES_FILEPATH = os.path.join(BASE_DIRPATH, 'player_names')
SCENARIO_NAMES_FILEPATH = os.path.join(BASE_DIRPATH, 'scenario_names')
SCENARIO_HASHES_FILEPATH = os.path.join(BASE_DIRPATH, 'scenario_hashes')
BATTLE_RESULTS_FILEPATH = os.path.join(BASE_DIRPATH, 'battle_results')


def load():
    manager = Manager()
    manager.load()
    return manager


class Manager:
    def __init__(self):
        # Local cache
        self.player_names_cache = cache.Cache(
            PLAYER_NAMES_FILEPATH,
            format=cache.Format.PICKLE,
        )
        self.scenario_names_cache = cache.Cache(
            SCENARIO_NAMES_FILEPATH,
            format=cache.Format.PICKLE,
        )
        self.scenario_hashes_cache = cache.Cache(
            SCENARIO_HASHES_FILEPATH,
            format=cache.Format.PICKLE,
        )
        self.battle_results_cache = cache.SplitCache(
            BATTLE_RESULTS_FILEPATH,
            format=cache.Format.PICKLE,
        )
        
        # In-memory storage
        self.player_names = []
        self.player_name_to_idx = {}

        self.scenario_names = []
        self.scenario_name_to_idx = {}

        self.scenario_hashes = []
        self.scenario_hash_to_idx = {}

        self.battle_results = []

        # Flags
        self._dirty_player_names = False
        self._dirty_scenario_names = False
        self._dirty_scenario_hashes = False
        self._dirty_battle_results = set()
        self.is_loaded = False

    def _latest_month(self):
        return max(self.battle_results.keys())

    def _latest_battle_results(self):
        return self.battle_results[self._latest_month()]

    def _next_id(self):
        if not self.battle_results:
            return _MIN_BATTLE_ID

        return self._latest_battle_results()[-1][0] + 1

    def _battle_to_tuple(self, x):
        return (
            x.id,
            x.start_time.timestamp(),
            x.duration_seconds,
            x.num_rounds,
            self.scenario_name_to_idx[x.scenario_name],
            None if x.scenario_hash is None else self.scenario_hash_to_idx[x.scenario_hash],
            _GAME_TYPE_TO_IDX.get(x.game_type),
            self.player_name_to_idx[x.player_names[0]],
            self.player_name_to_idx[x.player_names[1]],
            x.player_scores[0],
            x.player_scores[1],
            x.player_avg_hps[0],
            x.player_avg_hps[1],
            x.winner,
        )

    def _tuple_to_battle(self, x):
        return model.BattleResult(
            id=x[0],
            start_time=datetime.datetime.fromtimestamp(x[1], tz=datetime.timezone.utc),
            duration_seconds=x[2],
            num_rounds=x[3],
            scenario_name=self.scenario_names[x[4]],
            scenario_hash=None if x[5] is None else self.scenario_hashes[x[5]],
            quest=-1,
            game_type=_GAME_TYPES[x[6]],
            player_names=(self.player_names[x[7]], self.player_names[x[8]]),
            player_scores=(x[9], x[10]),
            player_avg_hps=(x[11], x[12]),
            winner=x[13],
        )

    def _add_battle(self, entry):
        if entry.player_names[0] not in self.player_name_to_idx:
            self.player_name_to_idx[entry.player_names[0]] = len(self.player_names)
            self.player_names.append(entry.player_names[0])
            self._dirty_player_names = True

        if entry.player_names[1] not in self.player_name_to_idx:
            self.player_name_to_idx[entry.player_names[1]] = len(self.player_names)
            self.player_names.append(entry.player_names[1])
            self._dirty_player_names = True

        if entry.scenario_name not in self.scenario_name_to_idx:
            self.scenario_name_to_idx[entry.scenario_name] = len(self.scenario_names)
            self.scenario_names.append(entry.scenario_name)
            self._dirty_scenario_names = True

        if entry.scenario_hash is not None and entry.scenario_hash not in self.scenario_hash_to_idx:
            self.scenario_hash_to_idx[entry.scenario_hash] = len(self.scenario_hashes)
            self.scenario_hashes.append(entry.scenario_hash)
            self._dirty_scenario_hashes = True

        month = f'{entry.start_time.year}-{entry.start_time.month:02}'
        battle = self._battle_to_tuple(entry)
        self._dirty_battle_results.add(month)
        self.battle_results.setdefault(month, []).append(battle)

        return battle

    async def download(self):
        """
        Download meta data from CH API and cache it locally.
        """

        os.makedirs(BASE_DIRPATH, exist_ok=True)

        # TODO: Use pager.to_next() once API supports it for battles
        # Download latest battle results from the API
        stop = False
        new_battles = []
        while not stop:
            async with aiohttp.ClientSession() as session:
                for _ in range(1000):
                    try:
                        pager = await api.search_battles(
                            session,
                            count=api.MAX_COUNT,
                            min_id=self._next_id(),
                        )
                    except api.RequestLimitReached:
                        stop = True
                        break

                    # Reached latest battle
                    if not pager.entries:
                        stop = True
                        break

                    for entry in pager.entries:
                        battle = self._add_battle(entry)
                        new_battles.append(battle)

            self.save()

        return new_battles

    def _reload_player_names(self):
        self.player_names_cache.reload()
        self.player_names = self.player_names_cache.data
        self.player_name_to_idx = {x: i for i, x in enumerate(self.player_names)}

    def _reload_scenario_names(self):
        self.scenario_names_cache.reload()
        self.scenario_names = self.scenario_names_cache.data
        self.scenario_name_to_idx = {x: i for i, x in enumerate(self.scenario_names)}

    def _reload_scenario_hashes(self):
        self.scenario_hashes_cache.reload()
        self.scenario_hashes = self.scenario_hashes_cache.data
        self.scenario_hash_to_idx = {x: i for i, x in enumerate(self.scenario_hashes)}

    def _reload_battle_results(self):
        self.battle_results_cache.reload()
        self.battle_results = self.battle_results_cache.data

    def load(self):
        """
        Load local meta data cache into memory.
        """

        if self.is_loaded:
            return

        self._reload_player_names()
        self._reload_scenario_names()
        self._reload_scenario_hashes()
        self._reload_battle_results()

        self.is_loaded = True

    def reload(self):
        self.is_loaded = False
        self.load()

    def save(self):
        if self._dirty_player_names:
            self.player_names_cache.save()
        self._dirty_player_names = False

        if self._dirty_scenario_names:
            self.scenario_names_cache.save()
        self._dirty_scenario_names = False

        if self._dirty_scenario_hashes:
            self.scenario_hashes_cache.save()
        self._dirty_scenario_hashes = False

        for key in self._dirty_battle_results:
            self.battle_results_cache.save(key)
        self._dirty_battle_results.clear()

    def iter_battle_results(self):
        return (x for month in sorted(self.battle_results) for x in self.battle_results[month])

    def iter_player_battle_results(self, player_idx):
        return (x for month in sorted(self.battle_results) for x in self.battle_results[month] if player_idx in x[7:9])

    def iter_h2h_battle_results(self, player_idx, opponent_idx):
        return (x for month in sorted(self.battle_results) for x in self.battle_results[month] if player_idx in x[7:9] and opponent_idx in x[7:9])


    ###########################
    # BATTLE RESULT UTILITIES #
    ###########################

    def is_casual(self, x):
        return _GAME_TYPES[x[6]] == 'CASUAL'

    def is_custom(self, x):
        return _GAME_TYPES[x[6]] == 'CUSTOM'

    def is_league(self, x):
        return _GAME_TYPES[x[6]] == 'LEAGUE'

    def is_ranked(self, x):
        return _GAME_TYPES[x[6]] == 'RANKED'

    def winner_idx(self, x):
        return x[7 + x[13]]

    def loser_idx(self, x):
        return x[7 + 1 - x[13]]

    def is_player(self, x, player_idx):
        return player_idx in x[7:9]

    def is_winner(self, x, player_idx):
        return self.winner_idx(x) == player_idx

    def is_loser(self, x, player_idx):
        return self.loser_idx(x) == player_idx

    def winner_name(self, x):
        return self.player_names[x[7 + x[13]]]

    def loser_name(self, x):
        return self.player_names[x[7 + 1 - x[13]]]

    def winner_score(self, x):
        return x[9 + x[13]]

    def loser_score(self, x):
        return x[9 + 1 - x[13]]

    def winner_avg_hp(self, x):
        return x[11 + x[13]]

    def loser_avg_hp(self, x):
        return x[11 + 1 - x[13]]

    def is_scenario(self, x, scenario_hash):
        idx = self.scenario_hash_to_idx.get(scenario_hash)
        return idx is not None and x[5] == idx

    def start_timestamp(self, x):
        return x[1]

    def end_timestamp(self, x):
        return x[1] + x[2]
