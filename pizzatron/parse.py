import re

from . import commands
from . import maps
from . import parse_util


NAME = 'pizzatron'
MENTION = '@' + NAME
TRIGGER = re.compile(r'^([Pp][Ii][Zz][Zz][Aa][Tt][Rr][Oo][Nn]|[Pp][Tt])([^-\w].*)?$')


def get_text(message):
    text = message.content

    match = TRIGGER.search(text)
    if match:
        text = match.group(2) or ''
    elif MENTION in text:
        text = parse_util.after(text, MENTION)
    else:
        return None

    text = text.strip()
    text = re.compile(r'^[,.:;?!]+').sub('', text)
    text = text.strip()

    return text


def parse_command(args, raw_args):
    if not args:
        return commands.cmd_empty, [], args, [], raw_args
    return parse_util.parse_longest_match(commands.COMMAND_MAP, args, raw_args)


def parse_card(args, raw_args):
    return parse_util.parse_longest_match(maps.card_map, args, raw_args)


def parse_item(args, raw_args):
    return parse_util.parse_longest_match(maps.item_map, args, raw_args)


def parse_any(args, raw_args):
    return parse_util.parse_longest_match(maps.any_map, args, raw_args)


def parse(text: str):
    raw_args = text.split()
    args = parse_util.tokenize(text)

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
