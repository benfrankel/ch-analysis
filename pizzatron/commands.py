import gamedata
import optimize
from . import display
from . import parse
from . import parse_util


HELP = """
What can I do for you?
```
help        Display this help.
info        Display information about a card or item.
items       List items containing a given card.
optimize    Calculate an optimal deck from card weights.
```
Try some of these commands:
```
pt raging battler
pt bless
pt help optimize
pt optimize dwarf priest greater heal
```
"""


def try_get_card(args, raw_args):
    if not args:
        return None, None, None, 'Please specify a card.'

    card, _, args, _, raw_args = parse.parse_card(args, raw_args)
    if card is None:
        return None, None, None, f'Sorry, I don\'t recognize the card "{" ".join(raw_args)}".'

    return card, args, raw_args, None


def try_get_item(args, raw_args):
    if not args:
        return None, None, None, 'Please specify an item.'

    item, _, args, _, raw_args = parse.parse_item(args, raw_args)
    if item is None:
        return None, None, None, f'Sorry, I don\'t recognize the item "{" ".join(raw_args)}".'

    return item, args, raw_args, None


def try_get_any(args, raw_args):
    if not args:
        return None, None, None, 'Please specify something.'

    match, _, args, _, raw_args = parse.parse_any(args, raw_args)
    if match is None:
        return None, None, None, f'Sorry, I don\'t recognize "{" ".join(raw_args)}".'

    return match, args, raw_args, None


def build_cmd_unknown(cmd_name, extra=''):
    async def cmd_unknown(args, raw_args):
        return f'Unknown command "{cmd_name}"{extra}.'
    return cmd_unknown


async def cmd_empty(args, raw_args):
    return 'No command provided.'


async def cmd_help(args, raw_args):
    if args and args[0] == 'optimize':
        card_classes = '- ' + '\n- '.join(sorted(optimize.get_card_packs().keys()))
        return f'**Card Classes:**\n{card_classes}'

    return HELP


async def cmd_info(args, raw_args):
    match, _, _, error = try_get_any(args, raw_args)
    if match is not None:
        if isinstance(match, gamedata.ItemType):
            return display.item(match)
        elif isinstance(match, gamedata.CardType):
            return display.card(match)

    return error


async def cmd_items(args, raw_args):
    card, _, _, error = try_get_card(args, raw_args)
    if card is None:
        return error

    items = []
    for item in gamedata.get_items():
        if card in item.cards:
            items.append(item)

    return display.items(items, sort=True, highlight_card=lambda x: x == card)


async def cmd_optimize(args, raw_args):
    archetype = ' '.join(args[:2])
    args = args[2:]
    raw_args = raw_args[2:]

    card_pack_combo = {}
    while args:
        index, key = parse_util.longest_match(optimize.card_packs, args)
        if index is not None:
            card_pack = optimize.card_packs[key]
            args = args[index:]
            raw_args = raw_args[index:]
        else:
            card, args, raw_args, error = try_get_card(args, raw_args)
            if card is None:
                return error
            card_pack = {card.name: 1}

        weight = 1
        if raw_args:
            try:
                weight = float(raw_args[0])
                args = args[1:]
                raw_args = raw_args[1:]
            except ValueError:
                pass
        for card, value in card_pack.items():
            card_pack_combo.setdefault(card, 0)
            card_pack_combo[card] += value * weight

    score, num_traits, optimum = (await optimize.find(archetype, card_pack_combo))[0]
    stats = f'\n**Total value:** {score}\n**Number of traits:** {num_traits}\n**Average value:** {score / (36 - num_traits)}'
    items = display.items(optimum)

    return f'{stats}\n\n{items}'


async def cmd_pool(args, raw_args):
    ethereal_form = [
        'Ethereal Form',
        'Creature of the Night',
        'Traveling Curse',
        'Fly',
        'Curse of Fragility',
        'Beam of Hate',
        'Ancient Grudge',
        'Boo!',
        'Memory Loss',
        'Unholy Curse',
        'Acid Jet',
        'Hex of Dissolution',
        'Doom',
    ]

    lycanthropic_form = [
        'Lycanthropic Form',
        'Creature of the Night',
        'Mad Dog',
        'Monstrous Hide',
        'Lunging Bite',
        'Prowl',
        'Mighty Charge',
        'Vicious Bite',
        'Howl',
        'Vicious Thrust',
        'Massive Jaws',
        'Sundering Strike',
        'All Out Attack ',
    ]

    vampiric_form = [
        'Vampiric Form',
        'Creature of the Night',
        'Loner',
        'Swarm of Bats',
        'Consuming Touch',
        'Prowl',
        'Spear of Darkness',
        'Avenging Touch',
        'Enervating Touch',
        'Flight Aura',
        'Invigorating Touch',
        'Vampire\'s Kiss',
        'Sneaky Bloodsuck',
    ]

    zombie_form = [
        'Creature of the Night',
        'Shuffle',
        'Bludgeon',
        'Able Bludgeon',
        'Zombie Mob',
        'Brains!',
        'Infected Bite',
    ]

    def by_quality(card):
        quality = {
            'E': -3,
            'D': 0,
            'C': 3,
            'B': 6,
            'A': 9,
            'AA': 12,
            'AAA': 15,
        }[card.quality] + {
            '+': 1,
            '-': -1,
            '': 0,
        }[card.plus_minus]
        return quality, card.name

    def is_melee_laser(card):
        is_attack = 'Attack' in card.types
        is_melee_laser_type = (card.attack_type, card.damage_type) == ('Melee', 'Laser')
        is_implemented = card.status == 'Implemented'
        return is_attack and is_melee_laser_type and is_implemented

    push_the_button = [card.name for card in sorted(
        filter(is_melee_laser, gamedata.get_cards()),
        key=by_quality,
    )]

    def is_magic_laser(card):
        is_attack = 'Attack' in card.types
        is_magic_laser_type = (card.attack_type, card.damage_type) == ('Magic', 'Laser')
        is_implemented = card.status == 'Implemented'
        return is_attack and is_magic_laser_type and is_implemented

    pull_the_trigger = [card.name for card in sorted(
        filter(is_magic_laser, gamedata.get_cards()),
        key=by_quality,
    )]

    laser_malfunction = [
        'Drained Battery',
        'Battery Explosion',
        'Meltdown',
        'Laser Spray',
    ]

    def is_boost(card):
        is_attachment = 'AttachToSelfComponent' in card.components
        is_boost_ = 'Boost' in card.types
        is_implemented = card.status == 'Implemented'
        return is_attachment and is_boost_ and is_implemented

    boost = [card.name for card in sorted(
        filter(is_boost, gamedata.get_cards()),
        key=by_quality,
    )]

    def is_handicap(card):
        is_attachment = 'AttachToSelfComponent' in card.components
        is_handicap_ = 'Handicap' in card.types
        is_implemented = card.status == 'Implemented'
        return is_attachment and is_handicap_ and is_implemented

    handicap = [card.name for card in sorted(
        filter(is_handicap, gamedata.get_cards()),
        key=by_quality,
    )]

    pool_alias_map = {
        'ethereal form': ethereal_form,
        'ethereal': ethereal_form,
        'spirit form': ethereal_form,
        'spirit': ethereal_form,
        'ghost form': ethereal_form,
        'ghost': ethereal_form,
        'mediums garb': ethereal_form,
        'garb': ethereal_form,

        'lycanthropic form': lycanthropic_form,
        'lycanthropic': lycanthropic_form,
        'wolf form': lycanthropic_form,
        'wolf': lycanthropic_form,
        'howl': lycanthropic_form,

        'vampiric form': vampiric_form,
        'vampiric': vampiric_form,
        'vampire form': vampiric_form,
        'vampire': vampiric_form,
        'vamp form': vampiric_form,
        'vamp': vampiric_form,
        'vampire kiss': vampiric_form,
        'vamp kiss': vampiric_form,
        'kiss': vampiric_form,

        'zombie form': zombie_form,
        'zombie': zombie_form,
        'spark of undeath': zombie_form,

        'push the button': push_the_button,
        'push button': push_the_button,
        'push': push_the_button,
        'button': push_the_button,

        'pull the trigger': pull_the_trigger,
        'pull trigger': pull_the_trigger,
        'pull': pull_the_trigger,
        'trigger': pull_the_trigger,

        'laser malfunction': laser_malfunction,
        'malfunction': laser_malfunction,
        'laser fail': laser_malfunction,
        'fail': laser_malfunction,

        'genetic engineering': boost,
        'gene engineering': boost,
        'genetic': boost,
        'engineering': boost,
        'gene therapy': boost,
        'gene': boost,
        'therapy': boost,
        'boost': boost,

        'destructive purge': handicap,
        'destructive': handicap,
        'radiation bomb': handicap,
        'radiation bolt': handicap,
        'radiation': handicap,
        'rad bomb': handicap,
        'rad bolt': handicap,
        'rad': handicap,
        'handicap': handicap,
    }

    pool, _, args, _, raw_args = parse_util.parse_longest_match(pool_alias_map, args, raw_args)
    if pool is None:
        return f'Sorry, I don\'t recognize the card pool "{" ".join(raw_args)}".'

    return '- ' + '\n- '.join(pool)


COMMAND_MAP = {
    'help': cmd_help,

    'info': cmd_info,

    'items': cmd_items,

    'optimize': cmd_optimize,

    'pool': cmd_pool,
}
