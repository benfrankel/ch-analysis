import gamedata
from . import parse_util


ITEM_ALIAS_MAP = {
    'vp': 'vibrant pain',
    'ulrich': 'st ulrichs bones',
    'troll': 'trolls ire',
    'snitrick': 'snitricks last stand',
    'reaper': 'reapers scythe',
    'quinn': 'quinns buckler',
    'drewg': 'dark drewgs mace',
    'bjss': 'bejeweled shortsword',
    'aegis': 'aegis of the defender',
    'dds': 'deadly deadly staff',
    'asmod': 'asmods telekinetic chain',
    'approp': 'ring of appropriation',
    'skiljin': 'skull of savage iljin',
    'mordecai': 'mordecais staff of magma',
    'sensate': 'sensates ring',
    'zoltan': 'zoltans laser scourge',
    'snarlcub': 'snarlcub hide',
    'pergop': 'pergops slippers',
    'hawkwind': 'hawkwinds moccasins',
    'huetotl': 'huetotls firebrand',
    'xarol': 'st xarols mace',
    'vasyl': 'vasyls ectoplasmic raiments',
    'armorbane': 'armorbane pendant',
    'vollmond': 'vollmond boots',
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
    'hex': 'hex of dissolution',
    'grudge': 'ancient grudge',
    'flank': 'flanking move',
    'swarm': 'swarm of bats',
    'glob': 'glob of flame',
    'vspin': 'violent spin',
    'hypno': 'hypnotic beacon',
    'insight': 'elvish insight',
    'wellspring': 'unholy wellspring',
    'res hide': 'resistant hide',
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
