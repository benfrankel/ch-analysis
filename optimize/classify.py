from gamedata import data

import os.path
import json


card_classes_filename = os.path.join('localdata', 'card_classes.json')


card_classes = dict()


def load():
    cards = data.get_cards()

    # Built-in classes
    card_classes['trait'] = dict()
    card_classes['direct magic damage'] = dict()
    card_classes['direct magic range'] = dict()
    card_classes['direct melee damage'] = dict()
    card_classes['step movement'] = dict()
    card_classes['step damage'] = dict()

    # Populating built-in classes
    for card in cards:
        if 'trait' in card.card_params:
            card_classes['trait'][card.name] = 1
    for card in cards:
        is_attack = 'Attack' in card.types
        is_move = 'Move' in card.types
        is_melee = 'Melee' in card.attack_type
        is_magic = 'Magic' in card.attack_type
        is_targeted = 'TargetedDamageComponent' in card.components
        is_direct = card.components.get('TargetedDamageComponent', dict()).get('numberTargets', 1) == 1
        if is_attack and is_magic and is_targeted and is_direct:
            card_classes['direct magic damage'][card.name] = card.average_damage
            card_classes['direct magic range'][card.name] = card.max_range
        if is_attack and is_move:
            card_classes['step movement'][card.name] = card.components['StepComponent']['movePoints']
            card_classes['step damage'][card.name] = card.average_damage
        if is_attack and is_melee:
            card_classes['direct melee damage'][card.name] = card.average_damage

    # Custom classes
    with open(card_classes_filename) as f:
        card_classes_info = json.load(f)
        for name, info in card_classes_info.items():
            card_classes[name] = card_classes.get(name, dict())
            card_classes[name].update(info)


def is_card_class(name):
    name = ' '.join(name.split())
    return name in card_classes


def get_card_class(name):
    name = ' '.join(name.split())
    return card_classes[name]


def get_card_classes():
    return card_classes
