import json
import os.path

from gamedata import data


card_packs_filename = os.path.join('localdata', 'card_packs.json')


card_packs = dict()


is_loaded = False


def load():
    global is_loaded
    if is_loaded:
        return

    cards = data.get_cards()

    # Built-in classes
    card_packs['trait'] = dict()
    card_packs['direct magic damage'] = dict()
    card_packs['direct magic range'] = dict()
    card_packs['direct melee damage'] = dict()
    card_packs['step movement'] = dict()
    card_packs['step damage'] = dict()

    # Populating built-in classes
    for card in cards:
        if 'trait' in card.card_params:
            card_packs['trait'][card.name] = 1
    for card in cards:
        is_attack = 'Attack' in card.types
        is_move = 'Move' in card.types
        is_melee = 'Melee' in card.attack_type
        is_magic = 'Magic' in card.attack_type
        is_targeted = 'TargetedDamageComponent' in card.components
        is_direct = card.components.get('TargetedDamageComponent', dict()).get('numberTargets', 1) == 1
        if is_attack and is_magic and is_targeted and is_direct:
            card_packs['direct magic damage'][card.name] = card.average_damage
            card_packs['direct magic range'][card.name] = card.max_range
        if is_attack and is_move:
            card_packs['step movement'][card.name] = card.components['StepComponent']['movePoints']
            card_packs['step damage'][card.name] = card.average_damage
        if is_attack and is_melee:
            card_packs['direct melee damage'][card.name] = card.average_damage

    # Custom classes
    with open(card_packs_filename) as f:
        card_packs_info = json.load(f)
        for name, info in card_packs_info.items():
            card_packs[name] = card_packs.get(name, dict())
            card_packs[name].update(info)

    is_loaded = True


def is_card_pack(name):
    name = ' '.join(name.split())
    return name in card_packs


def get_card_pack(name):
    name = ' '.join(name.split())
    return card_packs[name]


def get_card_packs():
    return card_packs
