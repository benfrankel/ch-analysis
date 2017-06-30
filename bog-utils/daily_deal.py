#!/usr/bin/env python3.6

from . import scrape
from . import report
from .. import gamedata

import datetime


wishlist = [
    'Strongarm',
    'Ancient Linestaff'
]


def main():
    info = scrape.daily_deal()

    today = datetime.date.today().day
    if not info['done'] or int(info['date'].split('-')[1]) != today:
        raise RuntimeError(f'Daily Deal is not done for {info["date"]}')

    matches = [item for item in info['items'] if item in wishlist]
    gamedata.load()

    message = ''
    for match in matches:
        card_names = ', '.join([card.name for card in gamedata.get_item(match).cards])
        message += f'{match} in DD, {info["date"]} ({card_names})\n'

    if message:
        report.announce(message.strip())
        print(message.strip())
    else:
        print('Did not make an announcement\n\n', '\n'.join(info['items']), sep='')

if __name__ == '__main__':
    main()
