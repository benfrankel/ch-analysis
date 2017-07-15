from battle_history import data


def matchup_history(player, opponent):
    try:
        battles = data.load(player)
    except FileNotFoundError:
        try:
            battles = data.load(opponent)
        except FileNotFoundError:
            battles = data.download(player)

    def is_matchup(battle):
        return {battle['winner'][0], battle['loser'][0]} == {player, opponent}

    return filter(is_matchup, battles)
