# Object model for Card Hunter game data (cards, items, characters)


_EXPANSION_NAME_BY_ID = {
    0: 'Base',
    1: 'AotA',
    2: 'EttSC',
    3: 'AA',
    4: 'AI',
    5: 'CM',
    6: 'EC',
    7: 'CF',
}


# Card type (e.g. "Ouch!", "Sprint, Team!", "Amorphous Body")
class CardType:
    def __init__(self,
        id,
        name,
        short_name,
        types,
        attack_type,
        damage_type,
        damage,
        min_range,
        max_range,
        move_points,
        duration,
        trigger,
        keep,
        trigger_effect,
        trigger2,
        keep2,
        trigger_effect2,
        text,
        flavor_text,
        play_text,
        trigger_text,
        trigger_attempt_text,
        trigger_succeed_text,
        trigger_fail_text,
        trigger_text2,
        trigger_attempt_text2,
        trigger_succeed_text2,
        trigger_fail_text2,
        components,
        params,
        plus_minus,
        quality,
        quality_warrior,
        quality_priest,
        quality_wizard,
        quality_dwarf,
        quality_elf,
        quality_human,
        rarity,
        function_tags,
        attach_image,
        status,
        audio_key,
        audio_key2,
        expansion_id,
        level,
        slot_types,
        art,
    ):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.types = types
        self.attack_type = attack_type
        self.damage_type = damage_type
        self.damage = damage
        self.min_range = min_range
        self.max_range = max_range
        self.move_points = move_points
        self.duration = duration
        self.trigger = trigger
        self.keep = keep
        self.trigger_effect = trigger_effect
        self.trigger2 = trigger2
        self.keep2 = keep2
        self.trigger_effect2 = trigger_effect2
        self.text = text
        self.flavor_text = flavor_text
        self.play_text = play_text
        self.trigger_text = trigger_text
        self.trigger_attempt_text = trigger_attempt_text
        self.trigger_succeed_text = trigger_succeed_text
        self.trigger_fail_text = trigger_fail_text
        self.trigger_text2 = trigger_text2
        self.trigger_attempt_text2 = trigger_attempt_text2
        self.trigger_succeed_text2 = trigger_succeed_text2
        self.trigger_fail_text2 = trigger_fail_text2
        self.components = components
        self.params = params
        self.plus_minus = plus_minus
        self.quality = quality
        self.quality_warrior = quality_warrior
        self.quality_priest = quality_priest
        self.quality_wizard = quality_wizard
        self.quality_dwarf = quality_dwarf
        self.quality_elf = quality_elf
        self.quality_human = quality_human
        self.rarity = rarity
        self.function_tags = function_tags
        self.attach_image = attach_image
        self.status = status
        self.audio_key = audio_key
        self.audio_key2 = audio_key2
        self.expansion_id = expansion_id
        self.level = level
        self.slot_types = slot_types
        self.art = art

    @property
    def quality_value(self):
        return {
            'E': -3,
            'D': 0,
            'C': 3,
            'B': 6,
            'A': 9,
            'AA': 12,
            'AAA': 15,
        }[self.quality] + {
            '-': -1,
            '': 0,
            '+': 1,
        }[self.plus_minus]

    @property
    def rarity_value(self):
        return {
            '': -1,
            'Common': 0,
            'Uncommon': 1,
            'Rare': 2,
        }[self.rarity]

    @property
    def is_common(self):
        return self.rarity == 'Common'

    @property
    def is_uncommon(self):
        return self.rarity == 'Uncommon'

    @property
    def is_rare(self):
        return self.rarity == 'Rare'

    @property
    def average_damage(self):
        overload = self.get_component('OverloadComponent', 'overload', 0)
        return (self.damage or 0) + [0, 2, 3.5][overload // 3]

    @property
    def expansion_abbreviation(self):
        return _EXPANSION_NAME_BY_ID.get(self.expansion_id)

    @property
    def is_implemented(self):
        return self.status == 'Implemented'


    #############
    # CARD TYPE #
    #############

    @property
    def is_armor(self):
        return 'Armor' in self.types

    @property
    def is_assist(self):
        return 'Assist' in self.types

    @property
    def is_attack(self):
        return 'Attack' in self.types

    @property
    def is_block(self):
        return 'Block' in self.types

    @property
    def is_boost(self):
        return 'Boost' in self.types

    @property
    def is_handicap(self):
        return 'Handicap' in self.types

    @property
    def is_move(self):
        return 'Move' in self.types

    @property
    def is_utility(self):
        return 'Utility' in self.types

    @property
    def is_hybrid(self):
        return len(self.types) > 1

    
    ###############
    # ATTACK TYPE #
    ###############

    @property
    def is_melee(self):
        return self.attack_type == 'Melee'

    @property
    def is_magic(self):
        return self.attack_type == 'Magic'

    @property
    def is_projectile(self):
        return self.attack_type == 'Projectile'


    ##########
    # PARAMS #
    ##########

    # Must play first. Implies cantrip.
    # Example: Impetuous Heal
    @property
    def is_trait(self):
        return 'trait' in self.params

    # Must play first, after playing traits.
    # Example: Prestidigitation
    @property
    def is_mandatory(self):
        return 'mandatory' in self.params

    # Doesn't end turn.
    # Example: Quick Run
    @property
    def is_cantrip(self):
        return 'cantrip' in self.params or 'trait' in self.params

    # Example: Reliable Mail
    @property
    def is_unplayable(self):
        return 'unplayable' in self.params

    # Example: Cleansing Ray
    @property
    def is_unblockable(self):
        return 'unblockable' in self.params

    # Example: Warp Run
    @property
    def ignores_halt(self):
        return 'ignoreHalt' in self.params

    # Example: Warp Run
    @property
    def ignores_stun(self):
        return 'ignoreStun' in self.params

    # Example: Scan
    @property
    def is_free_action(self):
        return 'noActionPoint' in self.params

    # Example: Hot Spot
    @property
    def only_affects_terrain(self):
        return 'terrainOnly' in self.params

    # TODO: Really?
    # Example: Healing Beacon
    @property
    def is_colored_by_player(self):
        return 'playerRelative' in self.params

    # Example: Bash
    @property
    def is_stealthy(self):
        return 'dontProvokeTurn' in self.params

    # TODO: What is hideOnResolve?

    # Example: Cleansing Presence
    @property
    def only_affects_terrain_under_allies(self):
        return 'alliedOccupantsOnly' in self.params

    # Example: Scan
    @property
    def only_affects_terrain_under_enemies(self):
        return 'enemyOccupantsOnly' in self.params

    # Example: Officer's Harness == 0
    @property
    def end_round_count(self):
        prefix = 'endRoundCount='
        for param in self.params:
            if param.startswith(prefix):
                return int(param[len(prefix):])
        return 1

    @property
    def is_radioactive_card(self):
        return 'radioactive' in self.params

    @property
    def is_genetic_card(self):
        return 'genetic' in self.params

    # From Twist Minds
    @property
    def is_fungal_twist_card(self):
        return 'fungalTwist' in self.params

    @property
    def is_laser_malfunction_card(self):
        return 'overload' in self.params

    @property
    def is_werewolf_card(self):
        return 'werewolf' in self.params

    @property
    def is_spirit_card(self):
        return 'spirit' in self.params

    @property
    def is_vampire_card(self):
        return 'vampire' in self.params

    @property
    def is_zombie_card(self):
        return 'zombie' in self.params

    @property
    def is_pixie_card(self):
        return 'pixie' in self.params

    @property
    def is_sculptor_card(self):
        return 'sculptor' in self.params

    @property
    def is_pirate_card(self):
        return 'pirate' in self.params

    @property
    def is_form_card(self):
        return 'form' in self.params

    @property
    def is_walpurgis_form_card(self):
        return 'walpurgis' in self.params

    # From Hook
    @property
    def is_hook_card(self):
        return 'hook' in self.params

    # From Edible
    @property
    def is_meal_card(self):
        return 'meal' in self.params


    ##############
    # COMPONENTS #
    ##############

    def get_component(self, name, key, default=None):
        return self.components.get(name, {}).get(key, default)

    # Example: Burrow
    @property
    def is_step(self):
        return 'StepComponent' in self.components

    # Example: Icy Apparition
    @property
    def is_step_attack(self):
        return self.is_attack and self.is_step
    
    # Example: Vow of Poverty == 'Empty'
    @property
    def retain_card_name_filter(self):
        return self.get_component(
            'ModifyCardRetentionComponent',
            'retainCardNameFilter',
        )

    # Example: Forward Thinking == 1
    @property
    def retain_count_modifier(self):
        return self.get_component(
            'ModifyCardRetentionComponent',
            'modify',
            default=0,
        )

    # Example: Fumble == 1
    @property
    def self_discard_oldest_count(self):
        return self.get_component(
            'SelfDiscardOldestComponent',
            'discardNumber',
            default=0,
        )

    def to_json(self):
        return self.id

    @classmethod
    def from_json(cls, game, data):
        return game.cards_by_id[data]

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return self.name


# Item type (e.g. "Bejeweled Shortsword", "Staff of the Misanthrope", "Armorbane Pendant")
class ItemType:
    def __init__(self,
        id,
        name,
        short_name,
        rarity,
        level,
        intro_level,
        total_value,
        token_cost,
        cards,
        slot_type,
        slot_type_default,
        image_name,
        tags,
        expansion_id,
        manual_rarity,
        manual_value,
    ):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.rarity = rarity
        self.level = level
        self.intro_level = intro_level
        self.total_value = total_value
        self.token_cost = token_cost
        self.cards = cards
        self.slot_type = slot_type
        self.slot_type_default = slot_type_default
        self.image_name = image_name
        self.tags = tags
        self.expansion_id = expansion_id
        self.manual_rarity = manual_rarity
        self.manual_value = manual_value

    @property
    def expansion_abbreviation(self):
        return _EXPANSION_NAME_BY_ID.get(self.expansion_id)

    @property
    def is_default_item(self):
        return self.image_name.startswith('Default Item ')


    #############
    # SLOT TYPE #
    #############

    @property
    def is_weapon(self):
        return self.slot_type == 'Weapon'

    @property
    def is_divine_weapon(self):
        return self.slot_type == 'Divine Weapon'

    @property
    def is_staff(self):
        return self.slot_type == 'Staff'

    @property
    def is_helmet(self):
        return self.slot_type == 'Helmet'

    @property
    def is_divine_item(self):
        return self.slot_type == 'Divine Item'

    @property
    def is_arcane_item(self):
        return self.slot_type == 'Arcane Item'

    @property
    def is_heavy_armor(self):
        return self.slot_type == 'Heavy Armor'

    @property
    def is_divine_armor(self):
        return self.slot_type == 'Divine Armor'

    @property
    def is_robes(self):
        return self.slot_type == 'Robes'

    @property
    def is_shield(self):
        return self.slot_type == 'Shield'

    @property
    def is_boots(self):
        return self.slot_type == 'Boots'

    @property
    def is_martial_skill(self):
        return self.slot_type == 'Martial Skill'

    @property
    def is_divine_skill(self):
        return self.slot_type == 'Divine Skill'

    @property
    def is_arcane_skill(self):
        return self.slot_type == 'Arcane Skill'

    @property
    def is_elf_skill(self):
        return self.slot_type == 'Elf Skill'

    @property
    def is_human_skill(self):
        return self.slot_type == 'Human Skill'

    @property
    def is_dwarf_skill(self):
        return self.slot_type == 'Dwarf Skill'

    def to_json(self):
        return self.id

    @classmethod
    def from_json(cls, game, data):
        return game.items_by_id[data]

    def __contains__(self, card_type):
        return card_type in self.cards

    def __iter__(self):
        return iter(self.cards)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return self.name


# Character archetype (e.g. "Dwarf Warrior", "Elf Priest")
class CharacterArchetype:
    def __init__(self,
        name,
        character_type,
        role,
        race,
        description,
        default_move,
        default_figure,
        start_items,
        slot_types,
        levels,
    ):
        self.name = name
        self.character_type = character_type
        self.role = role
        self.race = race
        self.description = description
        self.default_move = default_move
        self.default_figure = default_figure
        self.start_items = start_items
        self.slot_types = slot_types
        self.levels = levels

    def slot_types_at_level(self, level):
        return tuple(slot_type for (slot_type, min_level) in zip(self.slot_types, self.levels) if min_level is None or level >= min_level)

    @property
    def race_code(self):
        return {
            'Dwarf': 'D',
            'Human': 'H',
            'Elf': 'E',
        }[self.race]

    @property
    def role_code(self):
        return {
            'Warrior': 'W',
            'Priest': 'P',
            'Wizard': 'Z',
        }[self.role]

    def to_json(self):
        return self.name

    @classmethod
    def from_json(cls, game, data):
        return game.get_archetype(data)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return self.name


# Campaign adventure (e.g. "Slub Gut's Sanctum", "Attack of the War Monkeys")
class Adventure:
    def __init__(
        self,
        name,
        id,
        display_name,
        set,
        zone,
        level,
        xp,
        tags,
        module_name,
        description,
        map_pos,
        prerequisite_flags,
        removal_flags,
        completion_flags,
        battle_loot_count,
        adventure_loot_count,
        first_time_loot,
        scenarios,
        chests,
    ):
        self.name = name
        self.id = id
        self.display_name = display_name
        self.set = set
        self.zone = zone
        self.level = level
        self.xp = xp
        self.tags = tags
        self.module_name = module_name
        self.description = description
        self.map_pos = map_pos
        self.prerequisite_flags = prerequisite_flags
        self.removal_flags = removal_flags
        self.completion_flags = completion_flags
        self.battle_loot_count = battle_loot_count
        self.adventure_loot_count = adventure_loot_count
        self.first_time_loot = first_time_loot
        self.scenarios = scenarios
        self.chests = chests

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return self.name
