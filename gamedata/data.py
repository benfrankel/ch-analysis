"""
Interface with Card Hunter databases.
"""

import csv
import os.path
import re
import urllib.request

from gamedata import model
from const import GAMEDATA_DIR, IMAGES_DIR

# URLs to access CH data
CH_LIVE_DOMAIN = 'http://live.cardhunter.com/'
CARDS_CSV_PATH = 'data/gameplay/Cards/Cards.csv'
ITEMS_CSV_PATH = 'data/gameplay/Equipment/Equipment.csv'
ITEM_IMG_PATH = 'assets/item_illustrations/'
ARCHETYPES_CSV_PATH = 'data/gameplay/CharacterArchetypes/CharacterArchetypes.csv'
ADVENTURES_CSV_PATH = 'data/gameplay/Adventures/Adventures.csv'

# Files where the data will be stored locally
CARDS_FILENAME = os.path.join(GAMEDATA_DIR, 'cards.csv')
ITEMS_FILENAME = os.path.join(GAMEDATA_DIR, 'items.csv')
ARCHETYPES_FILENAME = os.path.join(GAMEDATA_DIR, 'archetypes.csv')
ADVENTURES_FILENAME = os.path.join(GAMEDATA_DIR, 'adventures.csv')

# Dictionaries where the data will be stored in program memory
card_dict = {}
short_card_dict = {}
item_dict = {}
short_item_dict = {}
archetype_dict = {}
other_archetype_dict = {}
adventure_dict = {}

# Flags
is_loaded = False


def download():
    """
    Download live data from CH and store it locally.
    """
    if not os.path.exists(GAMEDATA_DIR):
        os.makedirs(GAMEDATA_DIR)

    # Request the .csv files from CH live
    cards_req = urllib.request.urlopen(CH_LIVE_DOMAIN + CARDS_CSV_PATH)
    items_req = urllib.request.urlopen(CH_LIVE_DOMAIN + ITEMS_CSV_PATH)
    archetypes_req = urllib.request.urlopen(CH_LIVE_DOMAIN + ARCHETYPES_CSV_PATH)
    adventures_req = urllib.request.urlopen(CH_LIVE_DOMAIN + ADVENTURES_CSV_PATH)

    # Convert the requests into text
    cards_csv = cards_req.read().decode('utf-8', 'ignore')
    items_csv = items_req.read().decode('utf-8', 'ignore')
    archetypes_csv = archetypes_req.read().decode('utf-8', 'ignore')
    adventures_csv = adventures_req.read().decode('utf-8', 'ignore')

    # Write the text to local files
    with open(CARDS_FILENAME, 'w') as f:
        f.write(cards_csv)

    with open(ITEMS_FILENAME, 'w') as f:
        f.write(items_csv)

    with open(ARCHETYPES_FILENAME, 'w') as f:
        f.write(archetypes_csv)

    with open(ADVENTURES_FILENAME, 'w') as f:
        f.write(adventures_csv)


def load():
    """
    Load local CH data into program memory.
    """
    global is_loaded
    if is_loaded:
        return

    # Convert to integer, None if this is impossible
    def to_int(s):
        try:
            return int(s)
        except ValueError:
            return None

    def convert(s):
        j = to_int(s)
        if j is None:
            return s
        return j

    if not os.path.isfile(CARDS_FILENAME):
        download()

    # Extract the info from every line of cards.csv, store it in a CardType object and add it to a temporary dictionary
    with open(CARDS_FILENAME, newline='') as f:
        cards = csv.reader(f, delimiter=',', quotechar='"')
        next(cards)
        next(cards)
        
        for card in cards:
            if not card:
                continue
            
            components = {}
            for i in range(28, 38, 2):
                if card[i]:
                    params = {}
                    
                    if card[i + 1]:
                        for param in card[i + 1].split(';'):
                            if '=' in param:
                                p, value = param.split('=')
                                params[p] = convert(value)
                            else:
                                params[param] = None
                    
                    components[card[i]] = params

            new_card = model.CardType(
                id_=to_int(card[0]),
                name=card[1],
                short_name=card[2],
                types=card[3].split(','),
                attack_type=card[4],
                damage_type=card[5],
                damage=to_int(card[6]),
                min_range=to_int(card[7]),
                max_range=to_int(card[8]),
                move_points=to_int(card[9]),
                duration=to_int(card[10]),
                trigger=to_int(card[11]),
                keep=to_int(card[12]),
                trigger_effect=card[13],
                trigger2=to_int(card[14]),
                keep2=card[15],
                trigger_effect2=card[16],
                text=card[17],
                flavor_text=card[18],
                play_text=card[19],
                trigger_text=card[20],
                trigger_attempt_text=card[21],
                trigger_succeed_text=card[22],
                trigger_fail_text=card[23],
                trigger_text2=card[24],
                trigger_attempt_text2=card[25],
                trigger_succeed_text2=card[26],
                trigger_fail_text2=card[27],
                components=components,
                card_params=card[38].split(';'),
                plus_minus=card[39],
                quality=card[40],
                quality_warrior=card[41],
                quality_priest=card[42],
                quality_wizard=card[43],
                quality_dwarf=card[44],
                quality_elf=card[45],
                quality_human=card[46],
                rarity=card[47],
                function_tags=card[48],
                attach_image=card[49],
                status=card[50],
                audio_key=card[51],
                audio_key2=card[52],
                from_set=to_int(card[53]),
                level=to_int(card[54]),
                slot_types=card[55].split(','),
                art=card[56],
            )

            global card_dict, short_card_dict

            card_dict[normalize(new_card.name)] = new_card
            short_card_dict[normalize(new_card.short_name)] = new_card

    # Extract the info from every line of items.csv, store it in a ItemType object, and add it to the dictionary
    # Use the item list to narrow down the set of cards to non-monster cards
    with open(ITEMS_FILENAME, newline='') as f:
        items = csv.reader(f, delimiter=',', quotechar='"')
        next(items)
        next(items)
        
        for item in items:
            if not item or item[19] == 'Treasure':
                continue
            
            cards = []
            for i in range(9, 15):
                if item[i] != '':
                    card = card_dict[normalize(item[i])]
                    cards.append(card)
            
            new_item = model.ItemType(
                id_=to_int(item[0]),
                name=item[1],
                short_name=item[2],
                rarity=item[3],
                level=to_int(item[4]),
                intro_level=to_int(item[5]),
                total_value=to_int(item[6]),
                token_cost=(to_int(item[7]), to_int(item[8])),
                cards=cards,
                slot_type=item[19],
                slot_type_default=item[20],
                image_name=item[21],
                tags=item[22],
                from_set=item[23],
                manual_rarity=to_int(item[24]),
                manual_value=to_int(item[25]),
            )
            
            global item_dict, short_item_dict
            
            item_dict[normalize(new_item.name)] = new_item
            short_item_dict[normalize(new_item.short_name)] = new_item

    # Extract the info from every line of archetypes.csv, store it in an Archetype object, and add it to the dictionary
    with open(ARCHETYPES_FILENAME, newline='') as f:
        archetypes = csv.reader(f, delimiter=',', quotechar='"')
        next(archetypes)
        next(archetypes)
        
        for arc in archetypes:
            if not arc or arc[0] == 'SicklyMule':
                continue
            
            new_archetype = model.CharacterArchetype(
                name=arc[0],
                character_type=arc[1],
                role=arc[2],
                race=arc[3],
                description=arc[4],
                default_move=arc[7],
                default_figure=arc[8],
                start_items=(item_dict[normalize(arc[9])], item_dict[normalize(arc[10])]),
                slot_types=tuple(arc[i] for i in range(11, 48, 4) if arc[i] != ''),
                levels=tuple(to_int(arc[i]) for i in range(12, 49, 4)),
            )
            
            global archetype_dict
            global other_archetype_dict
            
            archetype_dict[normalize(new_archetype.name)] = new_archetype
            other_archetype_name = '{} {}'.format(new_archetype.race, new_archetype.role)
            other_archetype_dict[normalize(other_archetype_name)] = new_archetype

    # Extract the info from every line of adventures.csv, store it in an Adventure object, and add it to the dictionary
    with open(ADVENTURES_FILENAME, newline='') as f:
        adventures = csv.reader(f, delimiter=',', quotechar='"')
        next(adventures)
        next(adventures)

        for adv in adventures:
            if not adv or adv[2] != 'adventure':
                continue

            new_adventure = model.Adventure(
                name=adv[0],
                id=adv[1],
                display_name=adv[3],
                set=to_int(adv[4]),
                zone=to_int(adv[6]),
                level=to_int(adv[7]),
                xp=to_int(adv[8]),
                tags=tuple(adv[9].split()),
                module_name=adv[10],
                description=adv[11],
                map_pos=(to_int(adv[12]), to_int(adv[13])),
                prerequisite_flags=tuple(filter(lambda x: x, adv[14].split(','))),
                removal_flags=tuple(filter(lambda x: x, adv[15].split(','))),
                completion_flags=tuple(filter(lambda x: x, adv[16].split(','))),
                battle_loot_count=to_int(adv[17]),
                adventure_loot_count=to_int(adv[18]),
                first_time_loot=tuple(filter(lambda x: x, adv[19:21])),
                scenarios=tuple(filter(lambda x: x, adv[27:37])),
                chests=tuple(filter(lambda x: x, adv[37:41])),
            )

            global adventure_dict

            adventure_dict[normalize(new_adventure.display_name)] = new_adventure

    is_loaded = True


def normalize(text: str):
    text = text.lower()
    text = re.compile(r'[^\sa-z0-9]').sub('', text)
    text = re.compile(r'\s+').sub(' ', text)
    return text


def get_card(name):
    name = normalize(name)
    if name in card_dict:
        return card_dict[name]
    if name in short_card_dict:
        return short_card_dict[name]
    raise KeyError("Unknown card '{}'".format(name))


def get_cards():
    return list(card_dict.values())


def is_card(name):
    name = normalize(name)
    return name in card_dict or name in short_card_dict


def get_item(name):
    name = normalize(name)
    if name in item_dict:
        return item_dict[name]
    if name in short_item_dict:
        return short_item_dict[name]
    raise KeyError("Unknown item '{}'".format(name))


def get_items():
    return list(item_dict.values())


def is_item(name):
    name = normalize(name)
    return name in item_dict or name in short_item_dict


def get_archetype(name):
    name = normalize(name)
    if name in archetype_dict:
        return archetype_dict[name]
    if name in other_archetype_dict:
        return other_archetype_dict[name]
    raise KeyError("Unknown archetype '{}'".format(name))


def get_archetypes():
    return list(archetype_dict.values())


def is_archetype(name):
    name = normalize(name)
    return name in archetype_dict or name in other_archetype_dict


def get_adventure(name):
    name = normalize(name)
    if name in adventure_dict:
        return adventure_dict[name]
    raise KeyError("Unknown adventure '{}'".format(name))


def get_adventures():
    return list(adventure_dict.values())


def is_adventure(name):
    name = normalize(name)
    return name in adventure_dict


def download_item_image(image_name):
    image_name = image_name.replace(' ', '%20').replace("'", '%27')
    img_path = os.path.join(IMAGES_DIR, image_name)
    urllib.request.urlretrieve(CH_LIVE_DOMAIN + ITEM_IMG_PATH + image_name, img_path)

    return img_path
