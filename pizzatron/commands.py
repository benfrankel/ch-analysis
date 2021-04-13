import gamedata
import optimize
from . import parse


def try_get_card(args):
    if not args:
        return [None, 'Please specify a card.']

    card, *_, = parse.parse_card(args, args)
    if card is None:
        return None, f'Sorry, I don\'t recognize the card "{" ".join(args)}".'

    return card, None


def try_get_item(args):
    if not args:
        return [None, 'Please specify an item.']

    item, *_, = parse.parse_item(args, args)
    if item is None:
        return None, f'Sorry, I don\'t recognize the item "{" ".join(args)}".'

    return item, None


def item_display_line(item):
    tokens = ''.join(['', '<:ZTokenBlue:430454485257682945>', '<:ZTokenYellow:430454485127790601>', ''][token] for token in item.token_cost)
    if tokens:
        tokens += ' '
    slot = {
        'Weapon': '<:FinalSword:831632368463773766>',
        'Divine Weapon': '<:Evensong:831632333182074890>',
        'Staff': '<:StaffSimple3:831632354816688129>',
        'Helmet': '<:CapSergeant:831630801325129789>',
        'Divine Item': '<:ExDivItemQ:831630789774409737>',
        'Arcane Item': '<:CahinAsmond:831632343995383849>',
        'Heavy Armor': '<:AluxMail:831629711003746305>',
        'Divine Armor': '<:BrilliantShroud:831630178580430868>',
        'Robes': '<:robespointycollar1:831645387126341652>',
        'Shield': '<:BucklerAbsorb:831630188235718717>',
        'Boots': '<:AA3:831630168703369296>',
        'Martial Skill': '<:SkillMartialAttackS:831634222107459644>',
        'Divine Skill': '<:SkillDivineHealerS:831634461534978138>',
        'Arcane Skill': '<:SkillArcaneFireS:831634222040088586>',
        'Elf Skill': '<:SkillElfInsightS:831634221810319402>',
        'Human Skill': '<:SkillHumanThinkerS:831634221809664002>',
        'Dwarf Skill': '<:SkillDwarfPersistanceS:831634222057652244>',
    }.get(item.slot_type, '')
    if slot:
        slot += ' '
    cards = ', '.join(card.name for card in item.cards)

    return f'{slot}{tokens}**{item.name}:** {cards}'


def cmd_unknown(args):
    return 'Unknown command.'


def cmd_empty(args):
    return 'Yes?'


def cmd_help(args):
    if args and args[0] == 'optimize':
        card_classes = '- ' + '\n- '.join(sorted(optimize.get_card_packs().keys()))
        return f'**Card Classes:**\n{card_classes}'

    return 'Cannot help yet.'


def cmd_cards(args):
    item, error = try_get_item(args)
    if item is None:
        return error

    return item_display_line(item)


def cmd_items(args):
    card, error = try_get_card(args)
    if card is None:
        return error

    items = []
    for item in gamedata.get_items():
        if card in item.cards:
            items.append(item)
    slot_order = [
        'Weapon',
        'Divine Weapon',
        'Staff',
        'Helmet',
        'Divine Item',
        'Arcane Item',
        'Heavy Armor',
        'Divine Armor',
        'Robes',
        'Shield',
        'Boots',
        'Martial Skill',
        'Divine Skill',
        'Arcane Skill',
        'Elf Skill',
        'Human Skill',
        'Dwarf Skill',
    ]
    items.sort(key=lambda x: (x.token_cost, slot_order.index(x.slot_type)))

    return '\n'.join(item_display_line(item) for item in items)


def cmd_optimize(args):
    archetype = ' '.join(args[:2])
    card_pack_input = ' '.join(args[2:])

    card_pack_combo = {}
    total_weight = 0
    for card_pack_input in card_pack_input.split(','):
        if '=' in card_pack_input:
            name, weight = card_pack_input.split('=')
            name = name.replace(':', '').strip()
            weight = float(weight.strip())
        else:
            name = card_pack_input.replace(':', '').strip()
            weight = 1
        if ':' in card_pack_input:
            card_pack = {name: weight}
        else:
            card_pack = optimize.get_card_pack(name)
        for card in card_pack:
            card_pack_combo[card] = card_pack_combo.get(card, 0) + weight * card_pack[card]
        total_weight += weight
    for card in card_pack_combo:
        card_pack_combo[card] /= total_weight

    score, num_traits, optimum = optimize.find(archetype, card_pack_combo)[0]
    stats = f'\n**Total value:** {score}\n**Number of traits:** {num_traits}\n**Average value:** {score / (36 - num_traits)}'
    items = '\n'.join(item_display_line(item) for item in optimum)

    return f'{stats}\n\n{items}'


COMMAND_MAP = {
    'help': cmd_help,

    'cards': cmd_cards,

    'items': cmd_items,

    'optimize': cmd_optimize,
}
