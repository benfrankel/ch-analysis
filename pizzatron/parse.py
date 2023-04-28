import re

from . import parse_util
import party


NAME = 'pizzatron'
MENTION = '@' + NAME
TRIGGER = re.compile(r'^\W?[Pp][Tt]([^-\w].*)?$', flags=re.DOTALL)

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
    'br': 'blind rage',
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
    'neb': 'negative energy being',
    'vspin': 'violent spin',
    'res hide': 'resistant hide',
    #'swarm': 'swarm of bats',

    # Easter eggs
    'sadge': 'desperate block',
}

ARCHETYPE_ALIAS_MAP = {
    'dwarf warrior': 'dwarf warrior',
    'dwarf war': 'dwarf warrior',
    'dorf warrior': 'dwarf warrior',
    'dorf war': 'dwarf warrior',
    'd warrior': 'dwarf warrior',
    'd war': 'dwarf warrior',
    'dwarrior': 'dwarf warrior',
    'dwar': 'dwarf warrior',
    
    'human warrior': 'human warrior',
    'human war': 'human warrior',
    'h warrior': 'human warrior',
    'h war': 'human warrior',
    'hwarrior': 'human warrior',
    'hwar': 'human warrior',
    
    'elf warrior': 'elf warrior',
    'elf war': 'elf warrior',
    'e warrior': 'elf warrior',
    'e war': 'elf warrior',
    'ewarrior': 'elf warrior',
    'ewar': 'elf warrior',
    
    'dwarf priest': 'dwarf priest',
    'dorf priest': 'dwarf priest',
    'd priest': 'dwarf priest',
    'dpriest': 'dwarf priest',
    
    'human priest': 'human priest',
    'h priest': 'human priest',
    'hpriest': 'human priest',
    
    'elf priest': 'elf priest',
    'e priest': 'elf priest',
    'epriest': 'elf priest',
    
    'dwarf wizard': 'dwarf wizard',
    'dwarf wiz': 'dwarf wizard',
    'dwarf mage': 'dwarf wizard',
    'dorf wizard': 'dwarf wizard',
    'dorf wiz': 'dwarf wizard',
    'dorf mage': 'dwarf wizard',
    'd wizard': 'dwarf wizard',
    'd wiz': 'dwarf wizard',
    'd mage': 'dwarf wizard',
    'dwizard': 'dwarf wizard',
    'dwiz': 'dwarf wizard',
    'dmage': 'dwarf wizard',
    
    'human wizard': 'human wizard',
    'human wiz': 'human wizard',
    'human mage': 'human wizard',
    'h wizard': 'human wizard',
    'h wiz': 'human wizard',
    'h mage': 'human wizard',
    'hwizard': 'human wizard',
    'hwiz': 'human wizard',
    'hmage': 'human wizard',
    
    'elf wizard': 'elf wizard',
    'elf wiz': 'elf wizard',
    'elf mage': 'elf wizard',
    'e wizard': 'elf wizard',
    'e wiz': 'elf wizard',
    'e mage': 'elf wizard',
    'ewizard': 'elf wizard',
    'ewiz': 'elf wizard',
    'emage': 'elf wizard',
}


def get_text(message):
    text = message.content

    match = TRIGGER.search(text)
    if match:
        text = match.group(1) or ''
    elif MENTION in text:
        text = parse_util.after(text, MENTION)
    else:
        return None

    text = text.strip()
    text = re.compile(r'^[,.:;?!]+').sub('', text)
    text = text.strip()

    return text


class Manager:
    def __init__(self):
        # Maps
        self.card_map = {}
        self.item_map = {}
        self.archetype_map = {}
        self.any_map = {}
        
        # Matchers
        self.card_matcher = parse_util.Matcher(
            self.card_map,
            
            allow_typo=True,
            typo_cutoff=0.85,
            typo_require_unique=True,
        
            allow_prefix=True,
            prefix_min_length=1,
            prefix_min_ratio=0.2,
            prefix_allow_typo=True,
            prefix_typo_cutoff=0.8,
        
            allow_substring=True,
            substring_min_length=3,
            substring_min_ratio=0.25,
        )
        self.item_matcher = parse_util.Matcher(
            self.item_map,
            
            allow_typo=True,
            typo_cutoff=0.85,
            typo_require_unique=True,
        
            allow_prefix=True,
            prefix_min_length=1,
            prefix_min_ratio=0.2,
            prefix_allow_typo=True,
            prefix_typo_cutoff=0.8,
        
            allow_substring=True,
            substring_min_length=3,
            substring_min_ratio=0.25,
        )
        self.any_matcher = parse_util.Matcher(
            self.any_map,
            
            allow_typo=True,
            typo_cutoff=0.85,
            typo_require_unique=True,
        
            allow_prefix=True,
            prefix_min_length=1,
            prefix_min_ratio=0.2,
            prefix_allow_typo=True,
            prefix_typo_cutoff=0.8,
        
            allow_substring=True,
            substring_min_length=3,
            substring_min_ratio=0.25,
        )
        self.archetype_matcher = parse_util.Matcher(
            self.archetype_map,
        
            allow_typo=True,
            typo_cutoff=0.9,
            typo_require_unique=True,
        )

        # Flags
        self.is_loaded = False

    def _reload_card_map(self, game):
        self.card_map = game.cards_by_name | game.cards_by_short_name
    
        # Include aliases
        for alias, card in CARD_ALIAS_MAP.items():
            self.card_map[alias] = self.card_map[card]
    
        self.card_matcher.set_options(self.card_map)

    def _reload_item_map(self, game):
        self.item_map = game.items_by_name | game.items_by_short_name
    
        # Include aliases
        for alias, item in ITEM_ALIAS_MAP.items():
            self.item_map[alias] = self.item_map[item]
    
        self.item_matcher.set_options(self.item_map)

    def _reload_archetype_map(self, game):
        self.archetype_map = game.archetypes_by_name | game.archetypes_by_other_name
    
        # Include aliases
        for alias, arch in  ARCHETYPE_ALIAS_MAP.items():
            self.archetype_map[alias] = self.archetype_map[arch]
    
        self.archetype_matcher.set_options(self.archetype_map)

    def _reload_any_map(self):
        self.any_map = self.card_map | self.item_map
    
        self.any_matcher.set_options(self.any_map)

    def load(self, game):
        if self.is_loaded:
            return
    
        self._reload_card_map(game)
        self._reload_item_map(game)
        self._reload_archetype_map(game)
        self._reload_any_map()
    
        self.is_loaded = True

    def reload(self, game):
        self.is_loaded = False
        self.load(game)


class ParseError(Exception):
    pass


# TODO: Pool, Player
class Parser:
    def __init__(self, game, parse, args, raw_args):
        self._game = game
        self._parse = parse

        self.args = args
        self.raw_args = raw_args

    def card(self):
        if not self.args:
            raise ParseError('Please specify a card.')

        match, self.args, self.raw_args = self._parse.card_matcher.parse(self.args, self.raw_args)
        if match is None:
            raise ParseError(f'Unknown card "{" ".join(self.raw_args)}".')

        return match

    def card_search(self):
        if not self.args:
            raise ParseError('Please specify a card search query.')

        query = ' '.join(self.args)
        results = self._parse.card_matcher.search(query, score_gap=100)
        if not results:
            raise ParseError(f'No card results found for "{" ".join(self.raw_args)}". Try double-checking your spelling.')

        self.args.clear()
        self.raw_args.clear()

        return results

    def item(self):
        if not self.args:
            raise ParseError('Please specify an item.')

        match, self.args, self.raw_args = self._parse.item_matcher.parse(self.args, self.raw_args)
        if match is None:
            raise ParseError(f'Unknown item "{" ".join(self.raw_args)}".')

        return match

    def item_search(self):
        if not self.args:
            raise ParseError('Please specify an item search query.')

        query = ' '.join(self.args)
        results = self._parse.item_matcher.search(query, score_gap=100)
        if not results:
            raise ParseError(f'No item results found for "{" ".join(self.raw_args)}". Try double-checking your spelling.')

        self.args.clear()
        self.raw_args.clear()

        return results

    def archetype(self):
        if not self.args:
            raise ParseError('Please specify a character archetype.')

        match, self.args, self.raw_args = self._parse.archetype_matcher.parse(self.args, self.raw_args)
        if match is None:
            raise ParseError(f'Unknown character archetype "{" ".join(self.raw_args)}".')

        return match

    def any(self):
        if not self.args:
            raise ParseError('Please specify something.')

        match, self.args, self.raw_args = self._parse.any_matcher.parse(self.args, self.raw_args)
        if match is None:
            raise ParseError(f'Sorry, I don\'t recognize "{" ".join(self.raw_args)}".')

        return match

    def any_search(self):
        if not self.args:
            raise ParseError('Please specify a search query.')

        query = ' '.join(self.args)
        results = self._parse.any_matcher.search(query, score_gap=100)
        if not results:
            raise ParseError(f'No results found for "{" ".join(self.raw_args)}". Try double-checking your spelling.')

        self.args.clear()
        self.raw_args.clear()

        return results

    def character(self):
        if not self.args:
            raise ParseError('Please provide a character code.')

        code = self.raw_args[0].split(';')[:-1]
        if len(code) < 3:
            raise ParseError('Missing metadata at start of character code (e.g. L18;D;W).')

        level, race, role, *items = code
        if level[0] != 'L':
            raise ParseError('Invalid metadata at start of character code (missing `L` prefix on level).')
        try:
            level = int(level[1:])
        except ValueError:
            raise ParseError(f'Invalid metadata at start of character code (invalid level "{level}").')
        try:
            race = {
                'D': 'Dwarf',
                'H': 'Human',
                'E': 'Elf',
            }[race]
        except KeyError:
            raise ParseError(f'Invalid metadata at start of character code (invalid race "{race}").')
        try:
            role = {
                'W': 'Warrior',
                'P': 'Priest',
                'Z': 'Wizard',
            }[role]
        except KeyError:
            raise ParseError(f'Invalid metadata at start of character code (invalid class "{role}").')
        for i in range(len(items)):
            try:
                items[i] = self._game.items_by_id[int(items[i])]
            except (ValueError, KeyError):
                raise ParseError(f'Invalid item ID "{items[i]}" in character code.')

        archetype = self._game.get_archetype(f'{race} {role}')

        num_slots = len(archetype.slot_types_at_level(level))
        max_slots = len(archetype.slot_types)
        if len(items) != num_slots and len(items) != max_slots:
            raise ParseError('Invalid number of items in character code.')

        del self.args[0]
        del self.raw_args[0]

        return party.Character(
            name=None,
            level=level,
            archetype=archetype,
            items=items,
        )

    def party(self, min_chars=1, max_chars=3):
        characters = []

        for _ in range(min_chars):
            characters.append(self.character())

        for _ in range(max_chars - min_chars):
            try:
                characters.append(self.character())
            except ParseError:
                break
        
        return party.Party(characters)
