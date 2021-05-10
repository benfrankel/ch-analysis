import difflib
import re

import gamedata
from . import commands


NAME = 'pizzatron'
MENTION = '@' + NAME
TRIGGER = re.compile(r'^([Pp][Ii][Zz][Zz][Aa][Tt][Rr][Oo][Nn]|[Pp][Tt])([^-\w].*)?$')

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

    global card_map
    global item_map
    global any_map

    gamedata.load()

    cards = gamedata.get_cards()
    card_map = {normalize(card.name): card for card in cards}
    for card in cards:
        if card.short_name:
            card_map[normalize(card.short_name)] = card
    for alias, card in CARD_ALIAS_MAP.items():
        card_map[alias] = card_map[card]

    items = gamedata.get_items()
    item_map = {normalize(item.name): item for item in items}
    for item in items:
        if item.short_name:
            item_map[normalize(item.short_name)] = item
    for alias, item in ITEM_ALIAS_MAP.items():
        item_map[alias] = item_map[item]

    any_map = card_map | item_map

    is_loaded = True


def after(s: str, substr: str):
    start = s.find(substr)
    if start == -1:
        return ''
    return s[start + len(substr):]


def get_text(message):
    text = message.content

    match = TRIGGER.search(text)
    if match:
        text = match.group(2) or ''
    elif MENTION in text:
        text = after(text, MENTION)
    else:
        return None

    text = text.strip()
    text = re.compile(r'^[,.:;?!]+').sub('', text)
    text = text.strip()

    return text


def normalize(text: str):
    text = text.lower()
    text = re.compile(r'[^\sa-z0-9]').sub('', text)
    text = re.compile(r'\s+').sub(' ', text)
    return text


def tokenize(text: str):
    return [normalize(word) for word in text.split()]


def match_key(key, options):
    if key in options:
        return key

    matches = difflib.get_close_matches(key, options, n=2, cutoff=0.85)
    if len(matches) == 1 and len(matches[0]):
        return matches[0]

    return None


def longest_match_index(options, args):
    current_match = None
    key = ''
    keys = []
    for i, arg in enumerate(args):
        key += arg

        if key in options:
            match = key
        else:
            match = match_key(key, options)
        if match is not None:
            if current_match != match:
                current_match = match
                keys = []
            keys.append(key)

        key += ' '

    if current_match is None:
        return None

    matches = difflib.get_close_matches(current_match, keys, n=1, cutoff=0.85)
    if not matches:
        return None
    match = matches[0]

    return match.count(' ') + 1


def longest_match_index_to_key(index, options, args):
    key = ' '.join(args[:index])
    if key in options:
        return key

    match = match_key(key, options)
    if match is not None:
        return match

    return None


def longest_match_key(options, args):
    index = longest_match_index(options, args)
    if index is None:
        return None

    return longest_match_index_to_key(index, options, args)


def longest_match_value(options, args):
    key = longest_match_key(options, args)
    if key is None:
        return None

    if key in options:
        return options[key]

    return None


def parse_longest_match(options, args, raw_args):
    if not args:
        return None, [], args, [], raw_args

    index = longest_match_index(options, args)
    if index is None:
        return None, [], args, [], raw_args

    left = args[:index]
    right = args[index:]
    raw_left = raw_args[:index]
    raw_right = raw_args[index:]
    name = match_key(' '.join(left), options)
    if name is None:
        return None, [], args, [], raw_args

    result = options[name]

    return result, left, right, raw_left, raw_right


def parse_command(args, raw_args):
    if not args:
        return commands.cmd_empty, [], args, [], raw_args
    return parse_longest_match(commands.COMMAND_MAP, args, raw_args)


def parse_card(args, raw_args):
    return parse_longest_match(card_map, args, raw_args)


def parse_item(args, raw_args):
    return parse_longest_match(item_map, args, raw_args)


def parse_any(args, raw_args):
    return parse_longest_match(any_map, args, raw_args)


def parse(text: str):
    raw_args = text.split()
    args = tokenize(text)

    command, command_args, remaining_args, raw_command_args, raw_remaining_args = parse_command(args, raw_args)
    if command is not None:
        return command, remaining_args, raw_remaining_args

    match, match_args, remaining_match_args, raw_match_args, raw_remaining_match_args = parse_any(args, raw_args)
    if match is not None:
        command, _, remaining_match_args, _, raw_remaining_match_args = parse_command(remaining_match_args, raw_remaining_match_args)
        if command is commands.cmd_empty:
            command = commands.cmd_info
        command = command or commands.build_cmd_unknown(' '.join(raw_remaining_match_args), extra=f' for "{match.name}"')
        return command, match_args + remaining_match_args, raw_match_args + raw_remaining_match_args

    return commands.build_cmd_unknown(' '.join(raw_args)), args, raw_args
