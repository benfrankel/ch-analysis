import os.path
import re

import cache
import gamedata
from . import const


EMOJI_FILEPATH = os.path.join(const.BASE_DIRPATH, 'emoji.json')


def load():
    manager = Manager()
    manager.load()
    return manager


class Manager:
    SLOT_ORDER = (
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
    )
    
    RARITY_ORDER = (
        'Common',
        'Uncommon',
        'Rare',
        'Epic',
        'Legendary',
    )

    TYPE_ORDER = (
        'Move',
        'Attack',
        'Assist',
        'Utility',
        'Armor',
        'Block',
        'Boost',
        'Handicap',
    )

    QUALITY_CODE_TO_NAME = {
        'E': 'Black',
        'D': 'Paper',
        'C': 'Bronze',
        'B': 'Silver',
        'A': 'Gold',
        'AA': 'Emerald',
        'AAA': 'Amethyst',
    }

    def __init__(self):
        # Local cache
        self.emoji_cache = cache.Cache(
            EMOJI_FILEPATH,
            format=cache.Format.JSON,
        )

        # In-memory storage
        self.emoji = {}

        # Flags
        self.is_loaded = False

    def _reload_emoji(self):
        self.emoji_cache.reload()
        self.emoji = self.emoji_cache.data

    def load(self):
        if self.is_loaded:
            return

        self._reload_emoji()

        self.is_loaded = True

    def reload(self):
        self.is_loaded = False
        self.load()

    def quality_name(self, quality_code):
        return self.QUALITY_CODE_TO_NAME.get(quality_code, '')
    
    def rarity_icon(self, rarity_name):
        return self.emoji.get('rarity', {}).get(rarity_name, '')
    
    def token_icon(self, token_id):
        return self.emoji.get('token', {}).get(str(token_id), '')
    
    def expansion_icon(self, expansion_id):
        return self.emoji.get('expansion', {}).get(str(expansion_id), '')
    
    def slot_icon(self, slot_name):
        return self.emoji.get('slot', {}).get(slot_name, '')
    
    def card_icon(self, card_type):
        return self.emoji.get('card', {}).get(card_type.name, '')
    
    def item_icon(self, item_type):
        return self.emoji.get('item', {}).get(item_type.image_name, '')
    
    def item_short(self, item_type):
        icon = self.item_icon(item_type) or self.slot_icon(item_type.slot_type)
        if icon:
            icon += ' '

        item_name = item_type.name
        
        return f'{icon}{item_name}'
    
    def item_long(self, item_type, highlight_card=None):
        if highlight_card is None:
            def highlight_card(_):
                return False
    
        slot = self.item_icon(item_type) or self.slot_icon(item_type.slot_type)
        if slot:
            slot += ' '
    
        rarity = self.rarity_icon(item_type.rarity)
        if rarity:
            rarity += ' '
    
        tokens = ''.join(self.token_icon(t) for t in item_type.token_cost)
        if tokens:
            tokens += ' '
    
        card_icons = [self.card_icon(c) for c in item_type.cards]
        card_icons = ''.join(card_icons) + ' ' if all(card_icons) else ''

        item_name = item_type.name
        
        card_names = ', '.join(f'{s}{c.name}{s}' for c in item_type.cards for s in ['__' if highlight_card(c) else ''])
    
        return f'{slot}{rarity}{card_icons}{tokens}**{item_name}:** {card_names}'

    def by_power_slot_rarity_name(self, item_type):
        return (
            item_type.token_cost,
            self.SLOT_ORDER.index(item_type.slot_type),
            self.RARITY_ORDER.index(item_type.rarity),
            item_type.name,
        )
    
    def sort_items(self, item_types):
        item_types.sort(key=self.by_power_slot_rarity_name)
    
    def items_long(self, item_types, sort=False, highlight_card=None):
        if sort:
            self.sort_items(item_types)
        return '\n'.join(self.item_long(i, highlight_card) for i in item_types)
    
    def card_short(self, card_type):
        icon = self.card_icon(card_type)
        if icon:
            icon += ' '

        card_name = card_type.name
        
        return f'{icon}{card_name}'
    
    def card_long(self, card_type):
        rarity = self.rarity_icon(card_type.rarity)
        
        quality = self.quality_name(card_type.quality) + card_type.plus_minus or '='
    
        icon = self.card_icon(card_type)
        if icon:
            icon += ' '

        card_name = card_type.name
    
        expansion = self.expansion_icon(card_type.expansion_id)
        if expansion:
            expansion = f' {expansion}'
    
        types = ' / '.join(card_type.types)
        if types:
            types = f' {types}.'
    
        attack_type = ' '.join([card_type.attack_type, card_type.damage_type]).strip()
        if attack_type:
            attack_type = f' {attack_type}.'
    
        action = ''
        if card_type.move_points is not None:
            action += f' Move {card_type.move_points}.'
        if card_type.damage is not None:
            action += f' Damage {card_type.damage}.'
        if card_type.max_range is not None:
            action += f' Range {card_type.max_range}.'
    
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
        text = re.sub(r'&nbsp;', ' ', text)
        text = '> ' + text.replace('\n', '\n> ')
    
        return f'{rarity} [{quality}] {icon}**{card_name}{expansion}:**{types}{attack_type}{action}\n{text}'

    def by_type_quality_name(self, card_type):
        return (
            tuple(self.TYPE_ORDER.index(t) for t in card_type.types),
            -card_type.quality_value,
            card_type.name,
        )

    def sort_cards(self, card_types):
        card_types.sort(key=self.by_type_quality_name)
    
    def cards_short(self, card_types, sort=False):
        if sort:
            self.sort_cards(card_types)

        card_icons = [self.card_icon(c) for c in card_types]
        card_icons = ''.join(card_icons) + ' ' if all(card_icons) else ''
        if card_icons:
            return card_icons

        card_names = ', '.join(c.name for c in card_types)
        return card_names
    
    def cards_long(self, card_types, sort=False):
        if sort:
            self.sort_cards(card_types)

        card_icons = [self.card_icon(c) for c in card_types]
        card_icons = ''.join(card_icons) + ' ' if all(card_icons) else ''
        if card_icons:
            card_icons += '\n'
    
        card_names = ', '.join(c.name for c in card_types)
    
        return f'{card_icons}{card_names}'
    
    def any_type(self, thing):
        if isinstance(thing, gamedata.ItemType):
            return 'Item'
        if isinstance(thing, gamedata.CardType):
            return 'Card'
        if isinstance(thing, gamedata.Archetype):
            return 'Archetype'
        
    def any_short(self, thing):
        if isinstance(thing, gamedata.ItemType):
            return self.item_short(thing)
        if isinstance(thing, gamedata.CardType):
            return self.card_short(thing)
        if isinstance(thing, gamedata.Archetype):
            return self.archetype_short(thing)
    
    def any_long(self, thing):
        if isinstance(thing, gamedata.ItemType):
            return self.item_long(thing)
        if isinstance(thing, gamedata.CardType):
            return self.card_long(thing)
        if isinstance(thing, gamedata.Archetype):
            return self.archetype_long(thing)
    
    def archetype_short(self, arch):
        return f'{arch.race_code}{arch.role_code}'
    
    def archetype_long(self, arch):
        return f'{arch.race} {arch.role}'
    
    def character_short(self, char):
        item_icons = [self.item_icon(i) for i in char.items]
        item_icons = ''.join(item_icons) if all(item_icons) else ''
        
        return item_icons or self.archetype_long(char.archetype)
    
    def character_long(self, char):
        title = f'**Level {char.level} - {self.archetype_long(char.archetype)}:**'
        
        return f'{title}\n{self.items_long(char.items)}'

    def character_code(self, char):
        item_codes = ';'.join(str(i.id) for i in char.items)
        
        return f'L{char.level};{char.archetype.race_code};{char.archetype.role_code};{item_codes};'
    
    def party_short(self, party):
        return ' — '.join(self.character_short(char) for char in party)
    
    def party_long(self, party):
        return '\n\n'.join(self.character_long(char) for char in party)

    def party_code(self, party):
        return '\n'.join(self.character_code(char) for char in party)
