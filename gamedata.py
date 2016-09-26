# This file interfaces with the CH databases.

import urllib.request
import csv

import model


# URLs to access CH databases.
ch_live = 'http://live.cardhunter.com/'
cards_url = 'data/gameplay/Cards/Cards.csv'
items_url = 'data/gameplay/Equipment/Equipment.csv'
archetypes_url = 'data/gameplay/CharacterArchetypes/CharacterArchetypes.csv'


# Dictionaries where the databases will be stored.
card_dict = dict()
short_card_dict = dict()
item_dict = dict()
short_item_dict = dict()
archetype_dict = dict()
other_archetype_dict = dict()


def download():
    """
    Download live data from CH and store it locally.
    """
    # Request the .csv files from CH live.
    cards_req = urllib.request.urlopen(ch_live + cards_url)
    items_req = urllib.request.urlopen(ch_live + items_url)
    archetypes_req = urllib.request.urlopen(ch_live + archetypes_url)

    # Convert the requests into text.
    cards_csv = cards_req.read().decode('utf-8', 'ignore')
    items_csv = items_req.read().decode('utf-8', 'ignore')
    archetypes_csv = archetypes_req.read().decode('utf-8', 'ignore')

    # Write the text to local files.
    with open('cards.csv', 'w') as f:
        f.write(cards_csv)

    with open('items.csv', 'w') as f:
        f.write(items_csv)

    with open('archetypes.csv', 'w') as f:
        f.write(archetypes_csv)


def load():
    """
    Load local CH data into program memory.
    """
    all_cards_dict = dict()

    # Convert to integer, None if this is impossible.
    def to_int(s):
        try:
            return int(s)
        except ValueError:
            return None

    # Extract the info from every line of cards.csv, store it in a CardType object, and add it to a temporary dictionary.
    with open('cards.csv', newline='') as f:
        cards = csv.reader(f, delimiter=',', quotechar='"')
        skip_line = 2
        for card_vals in cards:
            if not card_vals:
                continue
            if skip_line > 0:
                skip_line -= 1
                continue
            ID = to_int(card_vals[0])
            name = card_vals[1]
            short_name = card_vals[2]
            types = card_vals[3].split(',')
            attack_type = card_vals[4]
            damage_type = card_vals[5]
            damage = to_int(card_vals[6])
            min_range = to_int(card_vals[7])
            max_range = to_int(card_vals[8])
            move_points = to_int(card_vals[9])
            duration = to_int(card_vals[10])
            trigger = to_int(card_vals[11])
            keep = to_int(card_vals[12])
            trigger_effect = card_vals[13]
            trigger_effect2 = card_vals[14]
            text = card_vals[15]
            flavor_text = card_vals[16]
            play_text = card_vals[17]
            trigger_text = card_vals[18]
            trigger_attempt_text = card_vals[19]
            trigger_succeed_text = card_vals[20]
            trigger_fail_text = card_vals[21]
            trigger_text2 = card_vals[22]
            trigger_attempt_text2 = card_vals[23]
            trigger_succeed_text2 = card_vals[24]
            trigger_fail_text2 = card_vals[25]
            component1 = card_vals[26]
            params1 = card_vals[27]
            component2 = card_vals[28]
            params2 = card_vals[29]
            component3 = card_vals[30]
            params3 = card_vals[31]
            component4 = card_vals[32]
            params4 = card_vals[33]
            component5 = card_vals[34]
            params5 = card_vals[35]
            params = card_vals[36]
            plus_minus = card_vals[37]
            quality = card_vals[38]
            quality_warrior = card_vals[39]
            quality_priest = card_vals[40]
            quality_wizard = card_vals[41]
            quality_dwarf = card_vals[42]
            quality_elf = card_vals[43]
            quality_human = card_vals[44]
            rarity = card_vals[45]
            function_tags = card_vals[46]
            attach_image = card_vals[47]
            status = card_vals[48]
            audio_key = card_vals[49]
            audio_key2 = card_vals[50]
            from_set = to_int(card_vals[51])
            level = to_int(card_vals[52])
            slot_types = card_vals[53].split(',')
            art = card_vals[54]

            new_card = model.CardType(ID, name, short_name, types, attack_type, damage_type, damage, min_range,
                                      max_range, move_points, duration, trigger, keep, trigger_effect, trigger_effect2,
                                      text, flavor_text, play_text, trigger_text, trigger_attempt_text,
                                      trigger_succeed_text, trigger_fail_text, trigger_text2, trigger_attempt_text2,
                                      trigger_succeed_text2, trigger_fail_text2, component1, params1, component2,
                                      params2, component3, params3, component4, params4, component5, params5, params,
                                      plus_minus, quality, quality_warrior, quality_priest, quality_wizard,
                                      quality_dwarf, quality_elf, quality_human, rarity, function_tags, attach_image,
                                      status, audio_key, audio_key2, from_set, level, slot_types, art)
            all_cards_dict[new_card.name] = new_card

    # Extract the info from every line of items.csv, store it in a ItemType object, and add it to the dictionary.
    # Use the item list to narrow down the set of cards to non-monster cards.
    with open('items.csv', newline='') as f:
        items = csv.reader(f, delimiter=',', quotechar='"')
        skip_line = 2
        for item_vals in items:
            if not item_vals or item_vals[19] == 'Treasure':
                continue
            if skip_line > 0:
                skip_line -= 1
                continue
            cards = []
            for i in range(9, 15):
                if item_vals[i] != '':
                    card = all_cards_dict[item_vals[i]]
                    cards.append(card)
                    global card_dict
                    global short_card_dict
                    card_dict[card.name.lower()] = card
                    short_card_dict[card.short_name.lower()] = card
            ID = to_int(item_vals[0])
            name = item_vals[1]
            short_name = item_vals[2]
            rarity = item_vals[3]
            level = to_int(item_vals[4])
            intro_level = to_int(item_vals[5])
            total_value = to_int(item_vals[6])
            token_cost1 = to_int(item_vals[7])
            token_cost2 = to_int(item_vals[8])
            token_cost = [token_cost1, token_cost2]
            slot_type = item_vals[19]
            slot_type_default = item_vals[20]
            image_name = item_vals[21]
            tags = item_vals[22]
            from_set = item_vals[23]
            manual_rarity = to_int(item_vals[24])
            manual_value = to_int(item_vals[25])
            new_item = model.ItemType(ID, name, short_name, rarity, level, intro_level, total_value, token_cost, cards,
                                      slot_type, slot_type_default, image_name, tags, from_set, manual_rarity,
                                      manual_value)
            global item_dict
            global short_item_dict
            item_dict[new_item.name.lower()] = new_item
            short_item_dict[new_item.short_name.lower()] = new_item

    # Extract the info from every line of archetypes.csv, store it in an Archetype object, and add it to the dictionary.
    with open('archetypes.csv', newline='') as f:
        archetypes = csv.reader(f, delimiter=',', quotechar='"')
        skip_line = 2
        for archetype_vals in archetypes:
            if not archetype_vals or archetype_vals[0] == 'SicklyMule':
                continue
            if skip_line > 0:
                skip_line -= 1
                continue
            name = archetype_vals[0]
            character_type = archetype_vals[1]
            role = archetype_vals[2]
            race = archetype_vals[3]
            description = archetype_vals[4]
            default_move = archetype_vals[7]
            default_figure = archetype_vals[8]
            start_item1 = item_dict[archetype_vals[9].lower()]
            start_item2 = item_dict[archetype_vals[10].lower()]
            start_items = [start_item1, start_item2]
            slot1 = archetype_vals[11]
            level1 = to_int(archetype_vals[12])
            slot2 = archetype_vals[15]
            level2 = to_int(archetype_vals[16])
            slot3 = archetype_vals[19]
            level3 = to_int(archetype_vals[20])
            slot4 = archetype_vals[23]
            level4 = to_int(archetype_vals[24])
            slot5 = archetype_vals[27]
            level5 = to_int(archetype_vals[28])
            slot6 = archetype_vals[31]
            level6 = to_int(archetype_vals[32])
            slot7 = archetype_vals[35]
            level7 = to_int(archetype_vals[36])
            slot8 = archetype_vals[39]
            level8 = to_int(archetype_vals[40])
            slot9 = archetype_vals[43]
            level9 = to_int(archetype_vals[44])
            slot10 = archetype_vals[47]
            level10 = to_int(archetype_vals[48])
            slot_types = [slot1, slot2, slot3, slot4, slot5, slot6, slot7, slot8, slot9, slot10]
            levels = [level1, level2, level3, level4, level5, level6, level7, level8, level9, level10]
            new_archetype = model.CharacterArchetype(name, character_type, role, race, description, default_move,
                                                     default_figure, start_items, slot_types, levels)
            global archetype_dict
            global other_archetype_dict
            archetype_dict[new_archetype.name.lower()] = new_archetype
            other_archetype_dict[new_archetype.race.lower() + ' ' + new_archetype.role.lower()] = new_archetype


def get_card(name):
    name = ' '.join(name.lower().split())
    if name in card_dict:
        return card_dict[name]
    return short_card_dict[name]


def get_cards():
    return list(card_dict.values())


def is_card(name):
    name = ' '.join(name.lower().split())
    return name in card_dict or name in short_card_dict


def get_item(name):
    name = ' '.join(name.lower().split())
    if name in item_dict:
        return item_dict[name]
    return short_item_dict[name]


def get_items():
    return list(item_dict.values())


def is_item(name):
    name = ' '.join(name.lower().split())
    return name in item_dict or name in short_item_dict


def get_archetype(name):
    name = ' '.join(name.lower().split())
    if name in archetype_dict:
        return archetype_dict[name]
    return other_archetype_dict[name]


def get_archetypes():
    return list(archetype_dict.values())


def is_archetype(name):
    name = ' '.join(name.lower().split())
    return name in archetype_dict or name in other_archetype_dict
