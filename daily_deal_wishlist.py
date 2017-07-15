#!/usr/bin/env python3.6

import datetime
import subprocess

import gamedata
from util import scrape
from util.guild import chat


wishlist = [
    'Dark Drewg\'s Mace',
    'Chiro\'s Cursed Amulet',
    'Relic of the First Vampire',
    'Witch\'s Snare',
    'Epigenetic Eraser',
    'Hand of Melvelous',
    'Final Sword',
    'Snitrick\'s Last Stand',
    'Vibrant Pain',
    'Talissa\'s Trident',
    'The Lunginator',
    'Captain Cedric\'s Vow',
    'Strongarm',
    'Ozone Plates',
    'Snarlcub Hide',
    'Instant Snowman',
    'True Silver',
    'Flame Warper',
    'Wym\'s Spiteful Bucket',
    'Phantom Pain',
    'Vial of Spite',
    'Asmod\'s Telekinetic Chain',
    'Vasyl\'s Ectoplasmic Raiments',
]


def main():
    print('Scraping daily deal thread')
    info = scrape.daily_deal()

    now = datetime.datetime.now()
    now_s = f'{now:%m-%d-%Y}'

    if info['date'] != f'{now:%m-%d-%Y}':
        raise RuntimeError(f'Daily Deal is outdated; says {info["date"]} (checked {now_s})')

    if not info['done']:
        raise RuntimeError(f'Daily Deal is not done; says {info["date"]} (checked {now_s})')

    matches = [item for item in info['items'] if item in wishlist]

    print('Loading gamedata')
    gamedata.load()

    message = ''
    for match in matches:
        item = gamedata.get_item(match)
        card_names = '*' + '*, *'.join([card.name for card in item.cards]) + '*'
        image_name = item.image_name + '.png'
        print(f'Downloading image of {item.name}')
        image_path = gamedata.download_item_image(image_name)
        print('Uploading image to imgur')
        link = subprocess.check_output(f'imgur "{image_path}"', shell=True).decode('ascii')[:-1]
        message += f'**{match}** in DD, {now:%b. %m, %Y}. ({card_names}) [__{link}__]\n'

    print('Done!')

    if message:
        print('\nMaking announcement on Discord')
        chat.announce(message.strip())
        print(message.strip())
    else:
        print('\nNo item from wishlist today\n\n', '\n'.join(info['items']), sep='')

if __name__ == '__main__':
    main()
