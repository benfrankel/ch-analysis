import html
import re

import requests


DAILY_DEAL_URL = 'http://forums.cardhunter.com/threads/7405/'
LOOT_FAIRY_TRACKER_URL = 'http://ln.to/lfg'


def daily_deal():
    site = requests.get(DAILY_DEAL_URL)
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

    info = {
        'date': lines[0],
        'done': lines[1] == 'Done',
        'items': lines[2:16],
    }

    return info


def loot_fairy_tracker():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    }
    site = requests.get(LOOT_FAIRY_TRACKER_URL, headers=headers)
    text = site.text

    # Remove fluff
    text = text[text.find('Present</td>'):text.find('</table>')]
    text = text[text.find('<tr'):]

    # Remove redundant / unwanted data in table cells
    text = re.sub(r'<td[^>]*>([^<]|<[^t]|<t[^d]|<td[^ ])*?</td>', '', text)
    text = re.sub(r'</tr>', '', text)

    # Strip away remaining HTML artifacts
    delimiter = '<>'
    text = re.sub(r'<tr class=" *', '', text)
    text = re.sub(r'" *data-module-name="', delimiter, text)
    text = re.sub(r'">', '', text)

    # Split results
    lines = text.splitlines()
    table = [line.strip().split(delimiter) for line in lines if line.strip()]

    results = {}
    for row in table:
        results[html.unescape(row[1])] = {
            'even': None,
            'odd': None,
            'absent': False,
            'found': True,
        }[row[0]]

    return results
