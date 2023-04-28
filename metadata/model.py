# Object model for Card Hunter meta data (players, battles)

import datetime


# Player (a user account)
class Player:
    def __init__(self,
        name,
        rating,
        steam_id,
        kongregate_id,
        ranked_mp_games=None,
        ranked_mp_wins=None,
        ranked_ai_games=None,
        ranked_ai_wins=None,
    ):
        self.name = name
        self.rating = rating
        self.steam_id = steam_id
        self.kongregate_id = kongregate_id
        self.ranked_mp_games = ranked_mp_games
        self.ranked_mp_wins = ranked_mp_wins
        self.ranked_ai_games = ranked_ai_games
        self.ranked_ai_wins = ranked_ai_wins

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.name}")'

    def __str__(self):
        return self.name


# Battle result (MP battle, PvP or vs. AI)
class BattleResult:
    def __init__(self,
        id,
        start_time,
        duration_seconds,
        num_rounds,
        scenario_name,
        scenario_hash,
        # TODO: What is this?
        quest,
        game_type,
        player_names,
        player_scores,
        player_avg_hps,
        winner,
    ):
        self.id = id
        self.start_time = start_time
        self.duration_seconds = duration_seconds
        self.num_rounds = num_rounds
        self.scenario_name = scenario_name
        self.scenario_hash = scenario_hash
        self.quest = quest
        self.game_type = game_type
        self.player_names = player_names
        self.player_scores = player_scores
        self.player_avg_hps = player_avg_hps
        self.winner = winner

    @property
    def loser(self):
        return 1 - self.winner

    @property
    def winner_name(self):
        return self.player_names[self.winner]

    @property
    def loser_name(self):
        return self.player_names[self.loser]

    @property
    def winner_score(self):
        return self.player_scores[self.winner]

    @property
    def loser_score(self):
        return self.player_scores[self.loser]

    @property
    def winner_avg_hp(self):
        return self.player_avg_hps[self.winner]

    @property
    def loser_avg_hp(self):
        return self.player_avg_hps[self.loser]

    @property
    def end_time(self):
        return self.start_time + datetime.timedelta(seconds=self.duration_seconds)

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.player_names[0]}", "{self.player_names[1]}")'

    def __str__(self):
        return f'{self.player_names[0]} vs. {self.player_names[1]}'
