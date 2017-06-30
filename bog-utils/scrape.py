import requests
import re


def guild_seasons(guild_name):
    site = requests.get(f'http://cardhuntermeta.farbs.org/guildseasons.php?name={guild_name.replace(" ", "+")}')

    # First we'll get monthly placements
    text = site.text

    # Remove fluff
    text = text[text.find('<td>'):text.find('</table>')]

    # If the guild doesn't exist
    if not text:
        raise KeyError(f'The guild \'{guild_name}\' does not exist')

    # Extract monthly placements
    placements = [int(x[0]) for x in re.findall(r'([0-9]+)(st|nd|rd|th)', text)]
    pizza = [[0, 5, 4, 3, 2, 1][x] if x < 6 else 0 for x in placements]

    # Next we'll get per-player participation
    text = site.text

    # Remove fluff
    text = text[text.find('Season Contributions'):text.rfind('<div id="footer_wrapper">')]

    # Isolate season names
    def insert_pizza(match):
        return f'\n\n{match.groups()[0]}\n{pizza.pop(0)}'

    text = re.sub(r'Season Contributions - ([^<]+)', insert_pizza, text).strip('\n')

    # Strip away HTML elements
    text = re.sub(r'<[^>]+>', r',', text)

    # Remove table headers
    text = text.replace('Rank', '')
    text = text.replace('Player', '')
    text = text.replace('Total Games', '')
    text = text.replace('Win Rate', '')
    text = text.replace('Contribution', '')

    # Remove winrates and placings
    text = re.sub(r'[0-9]+%', r'', text)
    text = re.sub(r'[0-9]+(st|nd|rd|th)', r'', text)

    # Reduce commas
    text = re.sub(r',+', r',', text)

    # Put players on their own lines
    text = re.sub(r',([^,]+,-?[0-9]+,-?[0-9]+)', r'\n\1', text)

    # Remove trailing commas
    text = re.sub(r',(\n|\r)', r'\n', text).rstrip('\n')

    # Reorder from oldest to newest season
    seasons = text.split('\n\n')
    seasons.reverse()

    info = []
    for season in seasons:
        lines = season.split('\n')
        season_info = {'name': lines[0],
                       'pizza': int(lines[1]),
                       'players': []}
        for line in lines[2:]:
            player, games, contribution = line.split(',')
            season_info['players'].append((player, int(games), int(contribution)))
        info.append(season_info)

    return info


def daily_deal():
    site = requests.get('http://forums.cardhunter.com/threads/7405/')
    text = site.text

    text = text[text.find('<b>Date:</b>'):text.find('<span style="color: rgb(0, 0, 0)">')]

    # Strip away HTML elements
    text = re.sub(r'<[^>]+>', r'', text).strip()

    # Remove labels
    text = re.sub(r'[^:\s]+:\s*', r'', text)

    # Remove empty lines
    text = text.replace('\n\n', '\n')

    lines = text.splitlines()

    info = {'date': lines[0],
            'done': lines[1] == 'Done',
            'items': lines[2:]}

    return info
