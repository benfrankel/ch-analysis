import gamedata
from . import parse_util


ITEM_ALIAS_MAP = {
    'bjss': 'bejeweled shortsword',
    'dds': 'deadly deadly staff',
    'vp': 'vibrant pain',
    'skiljin': 'skull of savage iljin',
    'snitrick': 'snitricks last stand',
    #'aegis': 'aegis of the defender',
    #'approp': 'ring of appropriation',
    #'zoltan': 'zoltans laser scourge',
    #'xarol': 'st xarols mace',
}

CARD_ALIAS_MAP = {
    'gh': 'greater heal',
    'tk': 'telekinesis',
    'rts': 'ready to strike',
    'mf': 'mass frenzy',
    'uf': 'unholy frenzy',
    'ww': 'whirlwind',
    'wwe': 'whirlwind enemies',
    'bt': 'battlefield training',
    'abt': 'advanced battlefield training',
    'spr': 'short perplexing ray',
    'pr': 'perplexing ray',
    'em': 'elven maneuvers',
    'foa': 'flash of agony',
    'fs': 'firestorm',
    'aoa': 'all out attack',
    'vspin': 'violent spin',
    'res hide': 'resistant hide',
    #'swarm': 'swarm of bats',
}

is_loaded = False

card_map = {}
item_map = {}
any_map = {}


def load():
    global is_loaded
    if is_loaded:
        return

    gamedata.load()

    global card_map
    cards = gamedata.get_cards()
    card_map = {parse_util.normalize(card.name): card for card in cards}
    for card in cards:
        if card.short_name:
            card_map[parse_util.normalize(card.short_name)] = card
    for alias, card in CARD_ALIAS_MAP.items():
        card_map[alias] = card_map[card]

    global item_map
    items = gamedata.get_items()
    item_map = {parse_util.normalize(item.name): item for item in items}
    for item in items:
        if item.short_name:
            item_map[parse_util.normalize(item.short_name)] = item
    for alias, item in ITEM_ALIAS_MAP.items():
        item_map[alias] = item_map[item]

    global any_map
    any_map = card_map | item_map

    is_loaded = True
