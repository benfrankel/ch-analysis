# Verbose battle log extension events


# Helper function to display time
def display_seconds(sec):
    s = sec % 60
    m = sec // 60
    h, m = divmod(m, 60)
    return '{:02}:{:02}:{:02}'.format(h, m, s)

# Helper function to display cards
def display_card(ex):
    return '{} from {}'.format(ex.card_name, ex.item_name)

# Populate params via args
def populate(obj, params, args):
    if len(params) != len(args):
        raise TypeError('Expected {} arguments ({} given)'.format(len(params), len(args)))
    for param, arg in zip(params, args):
        setattr(obj, param, arg)

# Superclass for extension events
class Extension:
    def __init__(self, name, player_turn):
        self.name = name
        self.player_turn = player_turn

    def __str__(self):
        turn = ' '
        if self.player_turn != -1:
            turn = '{}'.format(self.player_turn)
        return '{} [{}]'.format(turn, self.name)

# Factory for extension events
def build_ex(name, *params, describe=None):
    class _ExCustom(Extension):
        def __init__(self, player_turn, *args):
            super().__init__(name, player_turn)
            populate(self, params, args)

        def __str__(self):
            description = ''
            if describe is not None:
                description = ' ' + describe(self)
            return super().__str__() + description
    
    return _ExCustom

# Superclass for card extension events
class CardExtension(Extension):
    def __init__(self, name, player_turn, original_player_index, original_group_index, player_index, group_index,
                 card_index, item_name, card_name):
        super().__init__('Card ' + name, player_turn)
        self.original_player_index = original_player_index
        self.original_group_index = original_group_index
        self.player_index = player_index
        self.group_index = group_index
        self.card_index = card_index
        self.item_name = item_name
        self.card_name = card_name

    def __str__(self):
        return super().__str__() + ' {}'.format(display_card(self))

# Factory for card extension events
def build_card_ex(action, *params, describe=None):
    class _CustomExCard(CardExtension):
        def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                     item_name, card_name, *args):
            super().__init__(action, player_turn, original_player_index, original_group_index, player_index, group_index,
                             card_index, item_name, card_name)
            populate(self, params, args)

        def __str__(self):
            description = ''
            if describe is not None:
                description = ' ' + describe(self)
            return super().__str__() + description

    return _CustomExCard

# Superclass for trigger extension events
class TriggerExtension(Extension):
    def __init__(self, name, player_turn, die_roll, required_roll, hard_to_block, easy_to_block):
        super().__init__('Trigger ' + name, player_turn)
        self.die_roll = die_roll
        self.required_roll = required_roll
        self.hard_to_block = hard_to_block
        self.easy_to_block = easy_to_block
        self.success = die_roll + easy_to_block - hard_to_block >= required_roll

    def __str__(self):
        trigger = 'Failed to trigger'
        if self.success:
            trigger = 'Successfully triggered'
        return super().__str__() + ' {}'.format(trigger)

# Factory for trigger extension events
def build_trigger_ex(location, *params, describe=None):
    class _CustomExTrigger(TriggerExtension):
        def __init__(self, player_turn, die_roll, required_roll, hard_to_block, easy_to_block, *args):
            super().__init__(location, player_turn, die_roll, required_roll, hard_to_block, easy_to_block)
            populate(self, params, args)

        def __str__(self):
            description = ''
            if describe is not None:
                description = ' ' + describe(self)
            return super().__str__() + description

    return _CustomExTrigger

ExCardPlay       = build_card_ex('Play')
ExCardDraw       = build_card_ex('Draw')
ExCardReveal     = build_card_ex('Reveal')
ExCardDiscard    = build_card_ex('Discard')
ExTriggerInHand  = build_trigger_ex('In Hand', 'player_index', 'group_index', 'card_index',
                                    describe=lambda m:'card {} of group {} of player {}'.format(
                                        m.card_index, m.group_index, m.player_index))
ExTriggerTrait   = build_trigger_ex('Trait', 'player_index', 'group_index',
                                    describe=lambda m:'trait attached to group {} of player {}'.format(
                                        m.group_index, m.player_index))
ExTriggerTerrain = build_trigger_ex('Terrain', 'square',
                                    describe=lambda m:'square {}'.format(
                                        m.square))
ExSelectTarget   = build_ex('Select Target', 'target_player_indices', 'target_group_indices',
                            describe=lambda m:'Selected groups {} of players {}'.format(
                                m.target_group_indices, m.target_player_indices))
ExSelectSquare   = build_ex('Select Square', 'square', 'facing',
                            describe=lambda m:'Selected square {} with facing {}'.format(
                                m.square, m.facing))
ExRNG            = build_ex('RNG', 'rands',
                            describe=lambda m:'Result: {}'.format(
                                m.rands))
ExMustTrait      = build_ex('Must Play Trait', 'player_index',
                            describe=lambda m:'Player {} must play trait'.format(
                                m.player_index))
ExNoTraits       = build_ex('No Traits')
ExMustDiscard    = build_ex('Must Discard', 'player_index', 'group_index',
                            describe=lambda m:'Group {} of player {} must discard'.format(
                                m.group_index, m.player_index))
ExNoDiscards     = build_ex('No Discards')
ExPass           = build_ex('Pass')
ExResign         = build_ex('Resign')
ExHandPeek       = build_ex('Hand Peek')
ExDeckPeek       = build_ex('Deck Peek')
ExStartTimer     = build_ex('Start Timer', 'player_index', 'remaining',
                            describe=lambda m:'{} remaining'.format(
                                display_seconds(m.remaining)))
ExStopTimer      = build_ex('Stop Timer', 'player_index', 'remaining',
                            describe=lambda m:'{} remaining'.format(
                                display_seconds(m.remaining)))
