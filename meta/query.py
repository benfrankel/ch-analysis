from . import data


def _load_either(player, opponent):
    try:
        return data.load_player(player)
    except FileNotFoundError:
        try:
            return data.load_player(opponent)
        except FileNotFoundError:
            return data.download(player)


def matchup_history(player, opponent):
    battles = _load_either(player, opponent)

    def is_matchup(battle):
        return {battle['winner'][0], battle['loser'][0]} == {player, opponent}

    return filter(is_matchup, battles)


def player_query(predicate):
    def wrapped(player):
        return filter(lambda battle: predicate(player, battle), data.load_player(player))
    return wrapped


def matchup_query(predicate):
    def wrapped(player, opponent):
        return filter(lambda battle: predicate(player, opponent, battle), matchup_history(player, opponent))
    return wrapped


@player_query
def highlights(player, battle):
    return len(battle['winner']) == len(battle['loser']) == 2


@player_query
def wins(player, battle):
    return battle['winner'][0] == player


@player_query
def blitz_wins(player, battle):
    return battle['winner'][0] == player and battle['blitz']


@player_query
def defeats(player, battle):
    return battle['loser'][0] == player


def blitz_defeats(player, battle):
    return battle['loser'][0] == player and battle['blitz']
