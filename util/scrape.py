import html
import re

import requests


def guild_seasons(guild_name):
    site = requests.get(f'http://cardhuntermeta.farbs.org/guildseasons.php?name={guild_name.replace(" ", "+")}')

    # First we'll get monthly placements
    text = site.text

    # Remove fluff
    text = text[text.find('<td>'):text.find('</table>')]

    # If the guild doesn't exist
    if not text:
        raise KeyError(f"The guild '{guild_name}' does not exist")

    # Extract monthly placements
    placements = [int(x[0]) for x in re.findall(r'([0-9]+)(st|nd|rd|th)', text)][1:]
    pizzas = reversed([[0, 5, 4, 3, 2, 1][x] if x < 6 else 0 for x in placements])

    # Next we'll get per-player participation
    text = site.text

    # Remove fluff
    text = text[text.find('Season Contributions'):text.rfind('<div id="footer_wrapper">')]

    # Isolate season names
    text = re.sub(r'Season Contributions - ([^<]+)', r'\n\n\1', text).strip('\n')

    # Strip away HTML elements
    text = re.sub(r'<[^>]+>', r',', text)

    # Remove table headers
    text = text.replace('Rank', '')
    text = text.replace('Player', '')
    text = text.replace('Total Games', '')
    text = text.replace('Win Rate', '')
    text = text.replace('Contribution', '')

    # Remove winrates and placings
    text = re.sub(r'[0-9]+%', '', text)
    text = re.sub(r'[0-9]+(st|nd|rd|th)', '', text)

    # Reduce commas
    text = re.sub(r',+', ',', text)

    # Put players on their own lines
    text = re.sub(r',([^,]+,-?[0-9]+,-?[0-9]+)', r'\n\1', text)

    # Remove trailing commas
    text = re.sub(r',(\n|\r)', '\n', text).rstrip('\n')

    # Reorder from oldest to newest season
    seasons = text.split('\n\n')
    seasons.reverse()

    info = []
    for pizza, season in zip(pizzas, seasons):
        lines = season.split('\n')
        season_info = {'name': lines[0],
                       'pizza': pizza,
                       'players': []}
        for line in lines[1:]:
            player, games, contribution = line.split(',')
            season_info['players'].append((player, int(games), int(contribution)))
        info.append(season_info)

    return info


def daily_deal():
    site = requests.get('http://forums.cardhunter.com/threads/7405/')
    text = site.text

    # Remove fluff
    text = text[text.find('<article>'):text.find('</article>')]

    # Strip away HTML elements
    text = re.sub(r'<[^>]+>', '', text).strip()

    # Remove labels
    text = re.sub(r'[^:\s]+:\s*', '', text)

    # Remove empty lines
    text = text.replace('\n\n', '\n')

    lines = text.splitlines()

    info = {'date': lines[0],
            'done': lines[1] == 'Done',
            'items': lines[2:16]}

    return info


def loot_fairy_tracker():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    }
    site = requests.get('http://sorcererers.dotq.org/loot-fairy.php', headers=headers)
    text = site.text

    # Remove fluff
    text = text[text.find('Present</td>'):text.find('</table>')]
    text = text[text.find('<tr'):]

    # Remove redundant / unwanted data in table cells
    text = re.sub(r'<td[^>]*>([^<]|<[^t]|<t[^d]|<td[^ ])*?</td>', '', text)

    # Strip away remaining HTML artifacts
    delimiter = '<>'
    text = re.sub(r'<tr class="', '', text)
    text = re.sub(r'" data-module-name="', delimiter, text)
    text = re.sub(r'"></tr>', '', text)

    # Split results
    lines = text.splitlines()
    table = [line.strip().split(delimiter) for line in lines]

    results = {}
    for row in table:
        results[html.unescape(row[1])] = {
            'even': None,
            'odd': None,
            'absent': False,
            'found': True,
        }[row[0]]

    return results


def _parse_battles_page(text):
    text = text[text.find("<td style='white-space:nowrap;'>"):text.find('\n<div id="footer_wrapper">')]

    # Get link to previous page, if it exists
    try:
        prev = re.findall(r'<a href="(\?page=prev[^"]*)"', text)[0]
    except IndexError:
        prev = False

    # Remove link HTML elements
    text = re.sub(r'</?a[^>]*>', '', text)

    # Compress remaining HTML elements
    text = re.sub(r'(<(/[^>]*|[^t>]|t[^r>]|tr[^>])*>)+', ';', text).strip()

    # Translate HTML character codes
    text = text.replace('&amp;', '&')

    # Split rows of the table
    lines = [line[1:-1] for line in text.split('<tr>')][:-1]
    battles = []

    for line in lines:
        try:
            date, result, contribution = line.split(';')
        except ValueError:
            continue
        contribution = int(contribution)
        blitz = ' blitzed ' in result and not contribution % 2
        if not blitz and ' defeated ' not in result:
            continue
        result = result[:-1]
        if blitz:
            winner, loser = result.split(' blitzed ')
        else:
            winner, loser = result.split(' defeated ')
        winner = winner.split(', ')
        loser = loser.split(', ')
        battles.append({'date': date,
                        'winner': winner,
                        'loser': loser,
                        'contribution': contribution,
                        'blitz': blitz})
        print(battles[-1])

    return prev, battles


def _parse_battles_since_page(end_url):
    base_url = 'http://cardhuntermeta.farbs.org/guildhistory.php'
    result = []

    count = 1
    while end_url:
        print()
        print(count, ':', f'{base_url}{end_url}')
        count += 1
        site = requests.get(f'{base_url}{end_url}')
        end_url, lines = _parse_battles_page(site.text)
        result.extend(lines)

    return result


def player_battles(player_name):
    return _parse_battles_since_page(f'?player={player_name}&page=last')


def all_battles():
    return _parse_battles_since_page(f'?page=last')
