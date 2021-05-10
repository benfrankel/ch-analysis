import itertools
import random

import asyncio

from optimize import classify
import gamedata


is_loaded = False


class ItemFinder:
    slot_hash = {
        'Weapon': 0,
        'Divine Weapon': 1,
        'Staff': 2,
        'Helmet': 3,
        'Heavy Armor': 4,
        'Divine Armor': 5,
        'Robes': 6,
        'Boots': 7,
        'Shield': 8,
        'Divine Item': 9,
        'Arcane Item': 10,
        'Martial Skill': 12,
        'Divine Skill': 13,
        'Arcane Skill': 13,
        'Elf Skill': 14,
        'Human Skill': 15,
        'Dwarf Skill': 16
    }

    def __init__(self):
        self.fail_cache = set()
        self.card_weights = {}
        self.slot_items = {}
        self.optimal = {}

    @staticmethod
    def convert(info):
        return [0 if val == -1 else val for val in info]

    @staticmethod
    def hash(slot_type, info):
        return 204 * info[0] + 68 * info[1] + 17 * info[2] + ItemFinder.slot_hash[slot_type]

    @staticmethod
    def infos(slot_type):
        main_slots = 'Divine Weapon', 'Weapon', 'Staff'
        if slot_type in main_slots:
            token_options = (2, 2), (2, 1), (1, 1), (1, 0), (0, 0)
        else:
            token_options = (2, -1), (1, -1), (0, -1)
        for major, minor in token_options:
            for trait_count in range(4):
                yield major, minor, trait_count

    def find(self, slot_type, info):
        hash_slot = ItemFinder.hash(slot_type, ItemFinder.convert(info))
        best_score = 0
        best_items = []
        for item in self.slot_items[slot_type]:
            if item.token_cost != info[:2]:
                continue
            if sum(card.name in trait_class for card in item) != info[2]:
                continue
            val = sum(self.card_weights.get(card.name, 0) for card in item)
            score = val
            if score == best_score:
                best_items.append(item)
            elif score > best_score:
                best_items = [item]
                best_score = score
        self.optimal[hash_slot] = [best_score, best_items]

    def find_all(self):
        for slot_type in set(self.slot_items):
            for info in ItemFinder.infos(slot_type):
                self.find(slot_type, info)
        self.update_cache()

    def update_cache(self):
        for slot_type in set(self.slot_items):
            for info in ItemFinder.infos(slot_type):
                info = ItemFinder.convert(info)
                hash_ = ItemFinder.hash(slot_type, info)
                score, options = self.optimal[hash_]
                not_found = not options
                outdone = any(score <= self.get(slot_type, (info[0], info[1], t))[0] and self.get(slot_type, (info[0], info[1], t))[1] for t in range(info[2] + 1, 4))
                if not_found or outdone:
                    self.fail_cache.add(hash_)

    def get(self, slot_type, info):
        hash_slot = ItemFinder.hash(slot_type, info)
        if hash_slot in self.optimal:
            return self.optimal[hash_slot]
        raise KeyError('Cannot get optimal items without finding them first.')


class CharacterFinder:
    def __init__(self, optimal_items):
        self.optimal_items = optimal_items
        self.optimal = {}

    def distrib(self, slot_types, token_slots, total_major, total_minor):
        if sum(token_slots) < total_major + total_minor:
            return
        if total_major == total_minor == 0:
            for trait_dis in itertools.product(range(4), repeat=len(token_slots)):
                if any(ItemFinder.hash(s, (0, 0, t)) in self.optimal_items.fail_cache for s, t in zip(slot_types, trait_dis)):
                    continue
                yield tuple((0, 0, t) for t in trait_dis)
            if len(token_slots) == 0:
                return
        if token_slots[0] == 1:
            token_options = (2, 0, 1, 0), (1, 0, 0, 1), (0, 0, 0, 0)
        else:  # token_slots[0] == 2:
            token_options = (2, 2, 2, 0), (2, 1, 1, 1), (1, 1, 0, 2), (1, 0, 0, 1), (0, 0, 0, 0)
        for major, minor, new_major, new_minor in token_options:
            net_major = total_major - new_major
            net_minor = total_minor - new_minor
            if net_major < 0 or net_minor < 0:
                continue
            for trait_count in range(4):
                if ItemFinder.hash(slot_types[0], (major, minor, trait_count)) in self.optimal_items.fail_cache:
                    continue
                for distrib in self.distrib(slot_types[1:], token_slots[1:], net_major, net_minor):
                    yield ((major, minor, trait_count),) + distrib

    async def find(self, archetype):
        main_slot = 'Weapon', 'Divine Weapon', 'Staff'
        total_major, total_minor = 4, 4
        token_slots = [2 if slot_type in main_slot else 1 for slot_type in archetype.slot_types]
        best_builds = []
        best_avg = 0
        for distrib in self.distrib(archetype.slot_types, token_slots, total_major, total_minor):
            build = []
            score = 0
            num_traits = 0
            for slot_type, info in zip(archetype.slot_types, distrib):
                major, minor, trait_count = info
                add_score, options = self.optimal_items.get(slot_type, (major, minor, trait_count))
                build.append(random.choice(options))
                score += add_score
                num_traits += trait_count
            else:
                avg = score / (36 - num_traits)
                if avg == best_avg:
                    best_builds.append([score, num_traits, build])
                elif avg > best_avg:
                    best_builds = [[score, num_traits, build]]
                    best_avg = avg
            await asyncio.sleep(0)
        self.optimal[archetype] = best_builds

    def get(self, archetype):
        if archetype in self.optimal:
            return self.optimal[archetype]
        raise KeyError('Cannot get optimal builds without finding them first.')


items = dict()
trait_class = dict()


def load():
    global is_loaded
    if is_loaded:
        return

    global items, trait_class

    gamedata.load()
    classify.load()
    items = gamedata.get_items()
    trait_class = classify.get_card_pack('trait')
    cycling_class = classify.get_card_pack('cycling')

    is_loaded = True


async def find(archetype, card_weights):
    archetype = gamedata.get_archetype(archetype)
    slot_items = {slot: list(filter(lambda item: item.slot_type == slot, items)) for slot in set(archetype.slot_types)}

    optimal_items = ItemFinder()
    optimal_items.slot_items = slot_items
    optimal_items.card_weights = card_weights
    optimal_items.find_all()

    optimal_char = CharacterFinder(optimal_items)
    await optimal_char.find(archetype)

    return optimal_char.optimal[archetype]
