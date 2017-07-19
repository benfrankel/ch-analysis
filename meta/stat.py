from collections import defaultdict

from . import data, query


def _net_win(player, battle):
    return 1 if battle['winner'][0] == player else -1


def _contribution(player, battle):
    return battle['contribution'] * _net_win(player, battle)


def _opponent(player, battle):
    return battle['winner'] if battle['winner'][0] != player else battle['loser']


def summary(player, battles):
    if not battles:
        return 'No games played'

    wins = list(filter(lambda battle: battle['winner'][0] == player, battles))
    blitz_wins = list(filter(lambda battle: battle['blitz'], wins))
    defeats = list(filter(lambda battle: battle['loser'][0] == player, battles))
    blitz_defeats = list(filter(lambda battle: battle['blitz'], defeats))

    return (
        f'Winrate: {100 * len(wins) // len(meta)}%\n'
        f'Win-Lose: {len(wins)}-{len(defeats)}\n'
        f'Extended W-L: {len(blitz_wins)}-{len(wins) - len(blitz_wins)}-{len(defeats) - len(blitz_defeats)}-{len(blitz_defeats)}'
    )


def matchup_summary(player, opponent):
    battles = list(query.matchup_history(player, opponent))
    return f'{player} vs {opponent}\n\n{summary(player, meta)}'


def player_summary(player):
    battles = list(data.load(player))
    return f'{player}\n\n{summary(player, meta)}'


def _player_ladder(player, score):
    battles = list(data.load(player))
    opponents = defaultdict(int)
    for battle in battles:
        opponent = _opponent(player, battle)
        if len(opponent) == 2:
            opponent = opponent[0]
            opponents[opponent] += score(player, battle)
    return '\n'.join(map(lambda x: ': '.join(str(a) for a in x), sorted(opponents.items(), key=lambda x: -x[1])))


def _guild_ladder(player, score):
    battles = list(data.load(player))
    guilds = defaultdict(int)
    for battle in battles:
        opponent = _opponent(player, battle)
        if len(opponent) == 2:
            opponent = opponent[1]
            guilds[opponent] += score(player, battle)
    return '\n'.join(map(lambda x: ': '.join(str(a) for a in x), sorted(guilds.items(), key=lambda x: -x[1])))


def contribution_player_ladder(player):
    return _player_ladder(player, _contribution)


def contribution_guild_ladder(player):
    return _guild_ladder(player, _contribution)


def net_win_player_ladder(player):
    return _player_ladder(player, _net_win)


def net_win_guild_ladder(player):
    return _guild_ladder(player, _net_win)
