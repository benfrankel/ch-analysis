import os

from util import scrape
from util.pastebin import paste


class Entity:
    def __init__(self, name):
        self.games_played = []
        self.contribution = []
        self.pizza = []
        self.name = name

    def init_season(self):
        self.games_played.append(0)
        self.contribution.append(0)
        self.pizza.append(0)

    def play(self, games_played):
        self.games_played[-1] += games_played

    def contribute(self, contribution):
        self.contribution[-1] += contribution

    def award_pizza(self, pizza):
        self.pizza[-1] += pizza

    def get_participation(self, season=-1):
        season %= len(self.contribution)
        c = self.contribution[season]
        g = self.games_played[season]
        return c + g / 4


class Player(Entity):
    def __init__(self, name):
        super().__init__(name)
        self.pizza_score = []

    def award_pizza(self, pizza):
        super().award_pizza(pizza)
        self.pizza_score[-1] -= pizza

    def init_season(self):
        super().init_season()
        if len(self.pizza_score) == 0:
            self.pizza_score.append(0)
        else:
            self.pizza_score.append(self.pizza_score[-1])


class Season:
    @staticmethod
    def pizza_to_placement(pizza):
        return 6 - pizza if pizza else -1

    def __init__(self, guild_name, name, pizza, players):
        self.guild_name = guild_name
        self.name = name
        self.pizza = pizza
        self.players = players

    def __str__(self):
        placement = ['First Place',
                     'Second Place',
                     'Third Place',
                     'Fourth Place',
                     'Fifth Place',
                     'No Pizza'][Season.pizza_to_placement(self.pizza) - 1]
        result = f'{self.name} - {self.guild_name}\n{placement} ({self.pizza} pizza)\n\n'
        for player in sorted(self.players, key=lambda x: x[0]):
            if player[1]:
                result += f'{player[0]}: {player[1]} awarded, {player[2]:.2f} remaining in account ({player[3]:+.2f})\n'
            else:
                result += f'{player[0]}: {player[2]:.2f} pizza in account ({player[3]:+.2f})\n'
        return result


class Guild(Entity):
    def __init__(self, name):
        super().__init__(name)
        self.players = []
        self.player_dict = dict()
        self.seasons = []

    def add_player(self, name):
        if name in self.player_dict:
            self.players.append(self.player_dict[name])
            return

        new_player = Player(name)
        for _ in range(len(self.pizza) - 1):
            new_player.init_season()
        self.players.append(new_player)
        self.player_dict[name] = new_player

    def remove_player(self, name):
        self.players.remove(self.player_dict[name])

    def end_season(self, season):
        self.award_pizza(season['pizza'])

        total_contrib = 0
        total_games = 0
        for name, games_played, contribution in season['players']:
            if name not in self.player_dict:
                self.add_player(name)
                self.player_dict[name].init_season()

            self.player_dict[name].play(games_played)
            self.player_dict[name].contribute(contribution)

            total_contrib += contribution
            total_games += games_played

        self.play(total_games)
        self.contribute(total_contrib)

        for player in self.players:
            player.pizza_score[-1] += self.pizza[-1] * player.get_participation() / self.get_participation()

        for _ in range(self.pizza[-1]):
            next_player = max(self.players, key=lambda x: x.pizza_score[-1])
            next_player.award_pizza(1)

        players = [(p.name,
                    p.pizza[-1],
                    p.pizza_score[-1],
                    p.pizza_score[-1] + p.pizza[-1] - (p.pizza_score[-2] if len(p.pizza_score) > 1 else 0))
                   for p in self.players if p.games_played[-1]]
        self.seasons.append(Season(self.name, season['name'], season['pizza'], players))

    def init_season(self):
        super().init_season()
        for player in self.players:
            player.init_season()

    def __str__(self):
        result = ''
        for season in self.seasons:
            result += str(season) + '\n\n'

        result += 'CONCLUSION\n\n'
        for player in sorted(self.player_dict.values(), key=lambda x: x.name):
            if player not in self.players:
                result += '(LEFT) '
            result += f'{player.name}: {sum(player.pizza)} awarded out of {sum(player.pizza) + player.pizza_score[-1]:.2f}\n'
        return result


def guild_history(guild_name, seasons):
    guild = Guild(guild_name)

    for season in seasons:
        guild.init_season()
        guild.end_season(season)

    return guild


def auto_summary(guild_name):
    seasons = scrape.guild_seasons(guild_name)
    guild = guild_history(guild_name, seasons)

    path = os.path.join('localdata', 'guild_pizza', guild_name)

    with open(path, 'w') as f:
        f.write(str(guild))

    link = paste(None, None, None, [path], False, True)

    if link is None or not link.startswith('http'):
        raise IOError(f'Failed to paste to pastebin. Received response \'{link}\'')

    return link, guild
