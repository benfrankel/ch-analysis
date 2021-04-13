import re

import gamedata
from . import commands


NAME = 'pizzatron'
MENTION = '@' + NAME
TRIGGER = re.compile(r'^([Pp][Ii][Zz][Zz][Aa][Tt][Rr][Oo][Nn]|[Pp][Tt])([^-\w].*)?$')


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
    return normalize(text).split()


def longest_match_index(options, args):
    longest = -1
    key = ''
    for i, arg in enumerate(args):
        key += arg
        if key in options:
            longest = i + 1
        key += ' '

    return longest


def parse_longest_match(options, args, raw_args):
    if not args:
        return None, [], args, [], raw_args

    index = longest_match_index(options, args)
    if index == -1:
        return None, [], args, [], raw_args

    left = args[:index]
    right = args[index:]
    raw_left = raw_args[:index]
    raw_right = raw_args[index:]
    name = ' '.join(left)

    result = options[name]

    return result, left, right, raw_left, raw_right


def parse_command(args, raw_args):
    if not args:
        return commands.cmd_empty, [], args, [], raw_args
    return parse_longest_match(commands.COMMAND_MAP, args, raw_args)


def parse_card(args, raw_args):
    cards = gamedata.get_cards()
    card_map = {normalize(card.name): card for card in cards}
    for card in cards:
        if card.short_name:
            card_map[normalize(card.short_name)] = card
    return parse_longest_match(card_map, args, raw_args)


def parse_item(args, raw_args):
    items = gamedata.get_items()
    item_map = {normalize(item.name): item for item in items}
    for item in items:
        if item.short_name:
            item_map[normalize(item.short_name)] = item
    return parse_longest_match(item_map, args, raw_args)


def parse(text: str):
    raw_args = text.split()
    args = normalize(text).split()

    command, command_args, remaining_args, raw_command_args, raw_remaining_args = parse_command(args, raw_args)
    if command is not None:
        return command, remaining_args, raw_remaining_args

    item, item_args, remaining_item_args, raw_item_args, raw_remaining_item_args = parse_item(args, raw_args)
    if item is not None:
        command, _, remaining_item_args, raw_remaining_item_args, _ = parse_command(remaining_item_args, raw_remaining_item_args)
        return command or commands.cmd_unknown, item_args + remaining_item_args, raw_item_args + raw_remaining_item_args

    card, card_args, remaining_card_args, raw_card_args, raw_remaining_card_args = parse_card(args, raw_args)
    if card is not None:
        command, _, remaining_card_args, raw_remaining_card_args, _ = parse_command(remaining_card_args, raw_remaining_card_args)
        return command or commands.cmd_unknown, card_args + remaining_card_args, raw_card_args + raw_remaining_card_args

    return commands.cmd_unknown, args, raw_args
