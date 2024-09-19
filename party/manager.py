import os.path

import cache
from . import model
from . import optimize


# Local cache paths
BASE_DIRPATH = os.path.join(cache.BASE_DIRPATH, 'party')

CARD_PACKS_FILEPATH = os.path.join(BASE_DIRPATH, 'card_packs.json')


def load(game):
    manager = Manager()
    manager.load(game)
    return manager


class Manager:
    def __init__(self):
        # Local cache
        self.card_packs_cache = cache.Cache(
            CARD_PACKS_FILEPATH,
            format=cache.Format.JSON,
        )

        # In-memory storage
        self._slot_items = {}

        self.card_packs = {}

        # Flags
        self.is_loaded = False

    def _populate_auto_packs(self, game):
        # Auto-generated card packs
        auto_packs = (
            'is trait',
            'is attached trait',
            'is attack',
            'is move',
            'direct magic damage',
            'direct magic range',
            'direct melee damage',
            'step movement',
            'step damage',
            'movement',
        )
        for name in auto_packs:
            self.card_packs.setdefault(name, {})
    
        # Populate auto-generated card packs
        for c in game.cards:
            if c.is_trait:
                if 'ReplaceDrawComponent' not in c.components:
                    self.card_packs['is trait'][c.name] = 1
                if 'AttachToSelfComponent' in c.components:
                    self.card_packs['is attached trait'][c.name] = 1
        for c in game.cards:
            is_direct = c.get_component('TargetedDamageComponent', 'numberTargets', 1) == 1
            if c.is_attack:
                self.card_packs['is attack'][c.name] = 1
            if c.is_attack and c.is_magic and is_direct:
                self.card_packs['direct magic damage'][c.name] = c.average_damage
                self.card_packs['direct magic range'][c.name] = c.max_range
            if c.is_move:
                self.card_packs['is move'][c.name] = 1
                # TODO: Require step attack? Or allow Tunnel / Burrow?
                if c.is_attack and c.is_step:
                    self.card_packs['step movement'][c.name] = c.components['StepComponent']['movePoints']
                    self.card_packs['movement'][c.name] = c.components['StepComponent']['movePoints']
                    self.card_packs['step damage'][c.name] = c.average_damage
                elif 'MoveTargetComponent' in c.components:
                    self.card_packs['movement'][c.name] = c.get_component('MoveTargetComponent', 'movePoints', 0)
                else:
                    self.card_packs['movement'][c.name] = c.move_points or 0
            if c.is_attack and c.is_melee:
                self.card_packs['direct melee damage'][c.name] = c.average_damage

    def _reload_card_packs(self, game):
        self.card_packs_cache.reload()
        self.card_packs = self.card_packs_cache.data
        self._populate_auto_packs(game)

    def load(self, game):
        if self.is_loaded:
            return

        self._slot_items = {s: [i for i in game.items if i.slot_type == s] for s in game.slot_types}

        self._reload_card_packs(game)

        self.is_loaded = True

    def reload(self, game):
        self.is_loaded = False
        self.load(game)

    async def optimize(self, archetype, card_weights):
        slot_items = {s: i for s, i in self._slot_items.items() if s in archetype.slot_types}

        optimal_items = optimize.ItemFinder()
        optimal_items.slot_items = slot_items
        optimal_items.card_weights = card_weights
        optimal_items.traits = self.card_packs['is trait'].keys()
        optimal_items.find_all()

        optimal_char = optimize.CharacterFinder(optimal_items)
        await optimal_char.find(archetype)

        return optimal_char.optimal[archetype]
