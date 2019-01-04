"""
Interface with Card Hunter databases.
"""

import os.path
import csv
import urllib.request

from gamedata import model
from const import GAMEDATA_DIR

# URLs to access CH databases
ch_live = 'http://live.cardhunter.com/'
cards_url = 'data/gameplay/Cards/Cards.csv'
items_url = 'data/gameplay/Equipment/Equipment.csv'
item_img_url = 'assets/item_illustrations/'
archetypes_url = 'data/gameplay/CharacterArchetypes/CharacterArchetypes.csv'

# Files where the databases will be stored locally
cards_filename = os.path.join(GAMEDATA_DIR, 'cards.csv')
items_filename = os.path.join(GAMEDATA_DIR, 'items.csv')
archetypes_filename = os.path.join(GAMEDATA_DIR, 'archetypes.csv')

# Dictionaries where the databases will be stored in program memory
card_dict = {}
short_card_dict = {}
item_dict = {}
short_item_dict = {}
archetype_dict = {}
other_archetype_dict = {}

# Flags
is_loaded = False

def download():
    """
    Download live data from CH and store it locally.
    """
    if not os.path.exists(GAMEDATA_DIR):
        os.makedirs(GAMEDATA_DIR)

    # Request the .csv files from CH live
    cards_req = urllib.request.urlopen(ch_live + cards_url)
    items_req = urllib.request.urlopen(ch_live + items_url)
    archetypes_req = urllib.request.urlopen(ch_live + archetypes_url)

    # Convert the requests into text
    cards_csv = cards_req.read().decode('utf-8', 'ignore')
    items_csv = items_req.read().decode('utf-8', 'ignore')
    archetypes_csv = archetypes_req.read().decode('utf-8', 'ignore')

    # Write the text to local files
    with open(cards_filename, 'w') as f:
        f.write(cards_csv)

    with open(items_filename, 'w') as f:
        f.write(items_csv)

    with open(archetypes_filename, 'w') as f:
        f.write(archetypes_csv)


def load():
    """
    Load local CH data into program memory.
    """
    global is_loaded
    if is_loaded:
        return

    all_cards_dict = dict()

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

    if not os.path.isfile(cards_filename):
        download()

    # Extract the info from every line of cards.csv, store it in a CardType object and add it to a temporary dictionary
    with open(cards_filename, newline='') as f:
        cards = csv.reader(f, delimiter=',', quotechar='"')
        skip_line = 2
        
        for card in cards:
            if not card:
                continue
            
            if skip_line > 0:
                skip_line -= 1
                continue
            
            components = {}
            for i in range(5):
                params = {}
                
                if card[2*i + 29]:
                    for param in card[2*i + 29].split(';'):
                        if '=' in param:
                            p, value = param.split('=')
                            params[p] = convert(value)
                        else:
                            params[param] = ''
                
                components[card[2*i + 28]] = params

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
                trigger2=card[15],
                keep2=card[16],
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
            
            all_cards_dict[new_card.name] = new_card

    # Extract the info from every line of items.csv, store it in a ItemType object, and add it to the dictionary
    # Use the item list to narrow down the set of cards to non-monster cards
    with open(items_filename, newline='') as f:
        items = csv.reader(f, delimiter=',', quotechar='"')
        skip_line = 2
        
        for item in items:
            if not item or item[19] == 'Treasure':
                continue
            
            if skip_line > 0:
                skip_line -= 1
                continue
            
            cards = []
            for i in range(9, 15):
                if item[i] != '':
                    card = all_cards_dict[item[i]]
                    cards.append(card)
                    
                    global card_dict, short_card_dict
                    
                    card_dict[card.name.lower()] = card
                    short_card_dict[card.short_name.lower()] = card
            
            new_item = model.ItemType(
                id_=to_int(item[0]),
                name=item[1],
                short_name=item[2],
                rarity=item[3],
                level=to_int(item[4]),
                intro_level=to_int(item[5]),
                total_value=to_int(item[6]),
                token_cost=[to_int(item[7]), to_int(item[8])],
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
            
            item_dict[new_item.name.lower()] = new_item
            short_item_dict[new_item.short_name.lower()] = new_item

    # Extract the info from every line of archetypes.csv, store it in an Archetype object, and add it to the dictionary
    with open(archetypes_filename, newline='') as f:
        archetypes = csv.reader(f, delimiter=',', quotechar='"')
        skip_line = 2
        
        for arc in archetypes:
            if not arc or arc[0] == 'SicklyMule':
                continue
            
            if skip_line > 0:
                skip_line -= 1
                continue
            
            new_archetype = model.CharacterArchetype(
                name=arc[0],
                character_type=arc[1],
                role=arc[2],
                race=arc[3],
                description=arc[4],
                default_move=arc[7],
                default_figure=arc[8],
                start_items=[item_dict[arc[9].lower()], item_dict[arc[10].lower()]],
                slot_types=tuple(arc[i] for i in range(11, 48, 4) if arc[i] != ''),
                levels=tuple(to_int(arc[i]) for i in range(12, 49, 4)),
            )
            
            global archetype_dict
            global other_archetype_dict
            
            archetype_dict[new_archetype.name.lower()] = new_archetype
            other_archetype_name = '{} {}'.format(new_archetype.race.lower(), new_archetype.role.lower())
            other_archetype_dict[other_archetype_name] = new_archetype

    is_loaded = True

def normalize_name(name):
    return ' '.join(name.strip().lower().split())

def get_card(name):
    name = normalize_name(name)
    if name in card_dict:
        return card_dict[name]
    if name in short_card_dict:
        return short_card_dict[name]
    raise KeyError("Unknown card '{}'".format(name))

def get_cards():
    return list(card_dict.values())

def is_card(name):
    name = normalize_name(name)
    return name in card_dict or name in short_card_dict

def get_item(name):
    name = normalize_name(name)
    if name in item_dict:
        return item_dict[name]
    if name in short_item_dict:
        return short_item_dict[name]
    raise KeyError("Unknown item '{}'".format(name))

def get_items():
    return list(item_dict.values())

def is_item(name):
    name = normalize_name(name)
    return name in item_dict or name in short_item_dict

def get_archetype(name):
    name = normalize_name(name)
    if name in archetype_dict:
        return archetype_dict[name]
    if name in other_archetype_dict:
        return other_archetype_dict[name]
    raise KeyError("Unknown archetype '{}'".format(name))

def get_archetypes():
    return list(archetype_dict.values())

def is_archetype(name):
    name = normalize_name(name)
    return name in archetype_dict or name in other_archetype_dict

def download_item_image(image_name):
    image_name = image_name.replace(' ', '%20').replace("'", '%27')
    img_path = os.path.join(GAMEDATA_DIR, image_name)
    urllib.request.urlretrieve(ch_live + item_img_url + image_name, img_path)

    return img_path
