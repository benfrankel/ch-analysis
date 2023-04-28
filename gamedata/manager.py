"""
Interface with Card Hunter databases.
"""

import os
import os.path
import re
import urllib.parse
import urllib.request

import cache
from . import model


# CH database endpoints
CH_LIVE_DOMAIN = 'http://live.cardhunter.com'
CH_BETA_DOMAIN = 'http://beta.cardhunter.com'

CARDS_CSV_PATH = '/data/gameplay/Cards/Cards.csv'
ITEMS_CSV_PATH = '/data/gameplay/Equipment/Equipment.csv'
ITEM_IMG_PATH = '/assets/item_illustrations'
ARCHETYPES_CSV_PATH = '/data/gameplay/CharacterArchetypes/CharacterArchetypes.csv'
ADVENTURES_CSV_PATH = '/data/gameplay/Adventures/Adventures.csv'

CARDS_CSV_URL = urllib.parse.urljoin(CH_BETA_DOMAIN, CARDS_CSV_PATH)
ITEMS_CSV_URL = urllib.parse.urljoin(CH_BETA_DOMAIN, ITEMS_CSV_PATH)
ITEM_IMG_URL = urllib.parse.urljoin(CH_BETA_DOMAIN, ITEM_IMG_PATH)
ARCHETYPES_CSV_URL = urllib.parse.urljoin(CH_LIVE_DOMAIN, ARCHETYPES_CSV_PATH)
ADVENTURES_CSV_URL = urllib.parse.urljoin(CH_BETA_DOMAIN, ADVENTURES_CSV_PATH)

# Local cache paths
BASE_DIRPATH = os.path.join(cache.BASE_DIRPATH, 'gamedata')
IMAGE_DIRPATH = os.path.join(BASE_DIRPATH, 'image')

CARDS_FILEPATH = os.path.join(BASE_DIRPATH, 'cards.csv')
ITEMS_FILEPATH = os.path.join(BASE_DIRPATH, 'items.csv')
ARCHETYPES_FILEPATH = os.path.join(BASE_DIRPATH, 'archetypes.csv')
ADVENTURES_FILEPATH = os.path.join(BASE_DIRPATH, 'adventures.csv')


def download():
    """
    Download game data from CH live and cache it locally.
    """
    
    os.makedirs(BASE_DIRPATH, exist_ok=True)

    # Download game data
    urllib.request.urlretrieve(CARDS_CSV_URL, CARDS_FILEPATH)
    urllib.request.urlretrieve(ITEMS_CSV_URL, ITEMS_FILEPATH)
    urllib.request.urlretrieve(ARCHETYPES_CSV_URL, ARCHETYPES_FILEPATH)
    urllib.request.urlretrieve(ADVENTURES_CSV_URL, ADVENTURES_FILEPATH)


def download_item_image(image_name):
    image_name = urllib.parse.quote_plus(f'{image_name}.png')
    image_url = urllib.parse.urljoin(ITEM_IMG_URL, image_name)
    image_path = os.path.join(IMAGE_DIRPATH, image_name)
    urllib.request.urlretrieve(image_url, image_path)

    return image_path


def load():
    manager = Manager()
    manager.load()
    return manager


# Convert to integer; None if not possible
def _to_int(s):
    try:
        return int(s)
    except:
        return None


# Convert to boolean; None if not possible
def _to_bool(s):
    return {
        'true': True,
        'false': False,
    }.get(s)


# Convert to integer or boolean; keep as string if not possible
def _convert(s):
    i = _to_int(s)
    if i is not None:
        return i

    b = _to_bool(s)
    if b is not None:
        return b

    return s


def _normalize(text: str):
    text = text.strip().lower()
    text = re.compile(r'[^\sa-z0-9]').sub('', text)
    text = re.compile(r'\s+').sub(' ', text)
    return text


def _card_from_entry(entry):
    components = {}
    for i in range(28, 38, 2):
        name = entry[i]
        params = entry[i + 1]
        
        if not name:
            continue

        if not params:
            components[name] = {}
            continue

        component = {}
        for param in params.split(';'):
            key, value, *_ = param.split('=', maxsplit=1) + [None]
            component[key] = _convert(value)

        components[name] = component

    function_tags = {}
    for param in entry[48].split(';'):
        key, value, *_ = param.split('=', maxsplit=1) + [None]
        function_tags[key] = _convert(value)

    return model.CardType(
        id=_to_int(entry[0]),
        name=entry[1],
        short_name=entry[2],
        types=tuple(entry[3].split(',')),
        attack_type=entry[4],
        damage_type=entry[5],
        damage=_to_int(entry[6]),
        min_range=_to_int(entry[7]),
        max_range=_to_int(entry[8]),
        move_points=_to_int(entry[9]),
        duration=_to_int(entry[10]),
        trigger=_to_int(entry[11]),
        keep=_to_int(entry[12]),
        trigger_effect=entry[13],
        trigger2=_to_int(entry[14]),
        keep2=_to_int(entry[15]),
        trigger_effect2=entry[16],
        text=entry[17],
        flavor_text=entry[18],
        play_text=entry[19],
        trigger_text=entry[20],
        trigger_attempt_text=entry[21],
        trigger_succeed_text=entry[22],
        trigger_fail_text=entry[23],
        trigger_text2=entry[24],
        trigger_attempt_text2=entry[25],
        trigger_succeed_text2=entry[26],
        trigger_fail_text2=entry[27],
        components=components,
        params=tuple(entry[38].split(';')),
        plus_minus=entry[39],
        quality=entry[40],
        quality_warrior=entry[41],
        quality_priest=entry[42],
        quality_wizard=entry[43],
        quality_dwarf=entry[44],
        quality_elf=entry[45],
        quality_human=entry[46],
        rarity=entry[47],
        function_tags=function_tags,
        attach_image=entry[49],
        status=entry[50],
        audio_key=entry[51],
        audio_key2=entry[52],
        expansion_id=_to_int(entry[53]),
        level=_to_int(entry[54]),
        slot_types=tuple(entry[55].split(',')),
        art=entry[56],
    )


def _item_from_entry(cards_by_name, entry):
    cards = []
    for card_name in entry[9:15]:
        if not card_name:
            continue

        card = cards_by_name[_normalize(card_name)]
        cards.append(card)

    return model.ItemType(
        id=_to_int(entry[0]),
        name=entry[1],
        short_name=entry[2],
        rarity=entry[3],
        level=_to_int(entry[4]),
        intro_level=_to_int(entry[5]),
        total_value=_to_int(entry[6]),
        token_cost=(_to_int(entry[7]), _to_int(entry[8])),
        cards=cards,
        slot_type=entry[19],
        slot_type_default=entry[20],
        image_name=entry[21],
        tags=entry[22],
        expansion_id=_to_int(entry[23]),
        manual_rarity=_to_int(entry[24]),
        manual_value=_to_int(entry[25]),
    )


def _archetype_from_entry(items_by_name, entry):
    return model.CharacterArchetype(
        name=entry[0],
        character_type=entry[1],
        role=entry[2],
        race=entry[3],
        description=entry[4],
        default_move=entry[7],
        default_figure=entry[8],
        start_items=(
            items_by_name[_normalize(entry[9])],
            items_by_name[_normalize(entry[10])],
        ),
        slot_types=tuple(x for x in entry[11:48:4] if x),
        levels=tuple(_to_int(x) for x in entry[12:49:4]),
    )


def _adventure_from_entry(entry):
    return model.Adventure(
        name=entry[0],
        id=entry[1],
        display_name=entry[3],
        set=_to_int(entry[4]),
        zone=_to_int(entry[6]),
        level=_to_int(entry[7]),
        xp=_to_int(entry[8]),
        tags=tuple(entry[9].split()),
        module_name=entry[10],
        description=entry[11],
        map_pos=(_to_int(entry[12]), _to_int(entry[13])),
        prerequisite_flags=tuple(x for x in entry[14].split(',') if x),
        removal_flags=tuple(x for x in entry[15].split(',') if x),
        completion_flags=tuple(x for x in entry[16].split(',') if x),
        battle_loot_count=_to_int(entry[17]),
        adventure_loot_count=_to_int(entry[18]),
        first_time_loot=tuple(x for x in entry[19:21] if x),
        scenarios=tuple(x for x in entry[27:37] if x),
        chests=tuple(x for x in entry[37:41] if x),
    )


class Manager:
    def __init__(self):
        # Local cache
        self.cards_cache = cache.Cache(
            CARDS_FILEPATH,
            format=cache.Format.CSV,
        )
        self.items_cache = cache.Cache(
            ITEMS_FILEPATH,
            format=cache.Format.CSV,
        )
        self.archetypes_cache = cache.Cache(
            ARCHETYPES_FILEPATH,
            format=cache.Format.CSV,
        )
        self.adventures_cache = cache.Cache(
            ADVENTURES_FILEPATH,
            format=cache.Format.CSV,
        )
        
        # In-memory storage
        self.cards = []
        self.cards_by_id = {}
        self.cards_by_name = {}
        self.cards_by_short_name = {}

        self.items = []
        self.items_by_id = {}
        self.items_by_name = {}
        self.items_by_short_name = {}

        self.archetypes = []
        self.archetypes_by_name = {}
        self.archetypes_by_other_name = {}

        self.adventures = []
        self.adventures_by_display_name = {}

        self.slot_types = set()
        
        # Flags
        self.is_loaded = False

    def _reload_cards(self):
        self.cards_cache.reload()

        self.cards = []
        self.cards_by_id = {}
        self.cards_by_name = {}
        self.cards_by_short_name = {}
        for entry in self.cards_cache.data[2:]:
            if not entry:
                continue
    
            card = _card_from_entry(entry)

            self.cards.append(card)
            self.cards_by_id[card.id] = card
            self.cards_by_name[_normalize(card.name)] = card
            if card.short_name:
                self.cards_by_short_name[_normalize(card.short_name)] = card

    def _reload_items(self):
        self.items_cache.reload()

        self.items = []
        self.items_by_id = {}
        self.items_by_name = {}
        self.items_by_short_name = {}
        for entry in self.items_cache.data[2:]:
            if not entry or entry[19] == 'Treasure':
                continue
    
            item = _item_from_entry(self.cards_by_name, entry)

            self.items.append(item)
            self.items_by_id[item.id] = item
            self.items_by_name[_normalize(item.name)] = item
            if item.short_name:
                self.items_by_short_name[_normalize(item.short_name)] = item

    def _reload_archetypes(self):
        self.archetypes_cache.reload()

        self.archetypes = []
        self.archetypes_by_name = {}
        self.archetypes_by_other_name = {}
        self.slot_types = set()
        for entry in self.archetypes_cache.data[2:]:
            if not entry or entry[0] == 'SicklyMule':
                continue
    
            archetype = _archetype_from_entry(self.items_by_name, entry)
            other_archetype_name = f'{archetype.race} {archetype.role}'

            self.archetypes.append(archetype)
            self.archetypes_by_name[_normalize(archetype.name)] = archetype
            self.archetypes_by_other_name[_normalize(other_archetype_name)] = archetype
            self.slot_types.update(archetype.slot_types)

    def _reload_adventures(self):
        self.adventures_cache.reload()

        self.adventures = []
        self.adventures_by_display_name = {}
        for entry in self.adventures_cache.data[2:]:
            if not entry or entry[2] != 'adventure':
                continue
    
            adventure = _adventure_from_entry(entry)

            self.adventures.append(adventure)
            self.adventures_by_display_name[_normalize(adventure.display_name)] = adventure

    def load(self):
        """
        Load local game data cache into memory.
        """
        
        if self.is_loaded:
            return
    
        self._reload_cards()
        self._reload_items()
        self._reload_archetypes()
        self._reload_adventures()
    
        self.is_loaded = True

    def reload(self):
        self.is_loaded = False
        self.load()

    def get_card(self, name):
        name = _normalize(name)
        if name in self.cards_by_name:
            return self.cards_by_name[name]
        if name in self.cards_by_short_name:
            return self.cards_by_short_name[name]
        raise KeyError("Unknown card '{}'".format(name))
    
    def is_card(self, name):
        name = _normalize(name)
        return name in self.cards_by_name or name in self.cards_by_short_name
    
    def get_item(self, name):
        name = _normalize(name)
        if name in self.items_by_name:
            return self.items_by_name[name]
        if name in self.items_by_short_name:
            return self.items_by_short_name[name]
        raise KeyError("Unknown item '{}'".format(name))
    
    def is_item(self, name):
        name = _normalize(name)
        return name in self.items_by_name or name in self.items_by_short_name
    
    def get_archetype(self, name):
        name = _normalize(name)
        if name in self.archetypes_by_name:
            return self.archetypes_by_name[name]
        if name in self.archetypes_by_other_name:
            return self.archetypes_by_other_name[name]
        raise KeyError("Unknown archetype '{}'".format(name))
    
    def is_archetype(self, name):
        name = _normalize(name)
        return name in self.archetypes_by_name or name in self.archetypes_by_other_name
    
    def get_adventure(self, name):
        name = _normalize(name)
        if name in self.adventures_by_display_name:
            return self.adventures_by_display_name[name]
        raise KeyError("Unknown adventure '{}'".format(name))
    
    def is_adventure(self, name):
        name = _normalize(name)
        return name in self.adventures_by_display_name

