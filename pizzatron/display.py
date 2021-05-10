import re


def rarity(rarity_name):
    return {
        'Common': '<:common:832569011060342804>',
        'Uncommon': '<:uncommon:832569022535958538>',
        'Rare': '<:rare:832569034104897576>',
        'Epic': '<:epic:832569045454815274>',
        'Legendary': '<:legendary:832569056506675261>',
    }.get(rarity_name, '')


def quality(quality_name):
    return {
        'E': 'Black',
        'D': 'Paper',
        'C': 'Bronze',
        'B': 'Silver',
        'A': 'Gold',
        'AA': 'Emerald',
        'AAA': 'Amethyst',
    }.get(quality_name, '')


def slot(slot_name):
    return {
        'Weapon': '<:Strongarm:832525850490175499>',
        'Divine Weapon': '<:Evensong:831632333182074890>',
        'Staff': '<:StaffBurningIce:832531029340061716>',
        'Helmet': '<:HelmetBucket1:832531820963692594>',
        'Divine Item': '<:DivineItemTalisman2:832524312631312434>',
        'Arcane Item': '<:ArcaneItemsJewel_1:832527988432044033>',
        'Heavy Armor': '<:ArmorReliable:832525040700096533>',
        'Divine Armor': '<:DivineArmorAdeptsHealingRobes:832527541985214484>',
        'Robes': '<:CapeOfDarkMagic:832525659121123348>',
        'Shield': '<:DuelersBuckler:832532657195188245>',
        'Boots': '<:BootCamp:832526444755681352>',
        'Martial Skill': '<:SkillMartialAttackS:831634222107459644>',
        'Divine Skill': '<:SkillDivineHealerS:831634461534978138>',
        'Arcane Skill': '<:SkillArcaneFireS:831634222040088586>',
        'Elf Skill': '<:SkillElfInsightS:831634221810319402>',
        'Human Skill': '<:SkillHumanThinkerS:831634221809664002>',
        'Dwarf Skill': '<:SkillDwarfPersistanceS:831634222057652244>',
    }.get(slot_name, '')


def token(token_value):
    return {
        1: '<:ZTokenBlue:430454485257682945>',
        2: '<:ZTokenYellow:430454485127790601>',
    }.get(token_value, '')


def item(item_type, highlight_card=None):
    if highlight_card is None:
        def highlight_card(_):
            return False

    slot_str = slot(item_type.slot_type)
    if slot_str:
        slot_str += ' '

    rarity_str = rarity(item_type.rarity)
    if rarity_str:
        rarity_str += ' '

    tokens_str = ''.join(token(t) for t in item_type.token_cost)
    if tokens_str:
        tokens_str += ' '

    cards = ', '.join(s + card.name + s for card in item_type.cards for s in ['__' if highlight_card(card) else ''])

    return f'{rarity_str}{slot_str}{tokens_str}**{item_type.name}:** {cards}'


def sort_items(item_types):
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

    rarity_order = [
        'Common',
        'Uncommon',
        'Rare',
        'Epic',
        'Legendary',
    ]

    item_types.sort(key=lambda x: (x.token_cost, slot_order.index(x.slot_type), rarity_order.index(x.rarity)))


def items(item_types, sort=False, highlight_card=None):
    if sort:
        sort_items(item_types)
    return '\n'.join(item(item_type, highlight_card) for item_type in item_types)


def card(card_type):
    quality_str = quality(card_type.quality) + card_type.plus_minus

    type_str = ' '.join([card_type.attack_type, card_type.damage_type]).strip()
    if type_str:
        type_str = f' {type_str}.'

    action_str = ''
    if card_type.move_points is not None:
        action_str += f' Move {card_type.move_points}.'
    if card_type.damage is not None:
        action_str += f' Damage {card_type.damage}.'
    if card_type.max_range is not None:
        action_str += f' Range {card_type.max_range}.'

    text = ''
    if card_type.text:
        text = card_type.text
    if card_type.trigger_text:
        if text:
            text += '\n\n'
        text += 'Trigger'
        if card_type.trigger is not None and card_type.trigger != 0:
            text += f' ({abs(card_type.trigger)}+)'
        text += f': {card_type.trigger_text}'
        if card_type.trigger_text2:
            text += '\n\nTrigger'
            if card_type.trigger2 is not None and card_type.trigger2 != 0:
                text += f' ({abs(card_type.trigger2)}+)'
            text += f': {card_type.trigger_text2}'

    if card_type.flavor_text:
        if text:
            text += '\n\n'
        text += f'_{card_type.flavor_text}_'

    text = re.sub(r'</?u>', '__', text)
    text = re.sub(r'</?i>', '*', text)
    text = re.sub(r'<br ?/?>', '\n', text)
    text = '> ' + text.replace('\n', '\n> ')

    return f'{rarity(card_type.rarity)} [{quality_str}] **{card_type.name}:**{type_str}{action_str}\n{text}'
