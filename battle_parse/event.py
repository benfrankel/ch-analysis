# Logged battle events


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
def populate(obj, params, args, kwargs):
    expected = len(params)
    given = len(args) + len(kwargs)
    if expected != given:
        raise TypeError('Expected {} arguments ({} given)'.format(expected, given))
    
    for param, arg in zip(params, args):
        setattr(obj, param, arg)

    remaining = set(params[len(args):])
    for kw, arg in kwargs.items():
        try:
            remaining.remove(kw)
        except KeyError:
            raise TypeError("Unexpected keyword argument '{}'".format(kw))
        setattr(obj, kw, arg)

# Superclass for message events
class Message:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '[{}]'.format(self.name)

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

# Superclass for card extension events
class CardExtension(Extension):
    def __init__(self,
        name,
        player_turn,
        original_player_index,
        original_group_index,
        player_index,
        group_index,
        card_index,
        item_name,
        card_name,
    ):
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

# Superclass for trigger extension events
class TriggerExtension(Extension):
    def __init__(self,
        name,
        player_turn,
        die_roll,
        required_roll,
        hard_to_block,
        easy_to_block
    ):
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

# Factory for message events
def build_msg(name, *params, describe=None):
    class _MsgCustom(Message):
        def __init__(self, *args, **kwargs):
            super().__init__(name)
            populate(self, params, args, kwargs)

        def __str__(self):
            description = ''
            if describe is not None:
                description = ' ' + describe(self)
            return super().__str__() + description

    return _MsgCustom

# Factory for extension events
def build_ex(name, *params, describe=None):
    class _ExCustom(Extension):
        def __init__(self, player_turn, *args, **kwargs):
            super().__init__(name, player_turn)
            populate(self, params, args, kwargs)

        def __str__(self):
            description = ''
            if describe is not None:
                description = ' ' + describe(self)
            return super().__str__() + description
    
    return _ExCustom

# Factory for card extension events
def build_card_ex(action, *params, describe=None):
    class _CustomExCard(CardExtension):
        def __init__(self,
            player_turn,
            player_index,
            group_index,
            card_index,
            original_player_index,
            original_group_index,
            item_name,
            card_name,
            *args,
            **kwargs,
        ):
            super().__init__(
                action,
                player_turn,
                original_player_index,
                original_group_index,
                player_index,
                group_index,
                card_index,
                item_name,
                card_name,
            )
            populate(self, params, args, kwargs)

        def __str__(self):
            description = ''
            if describe is not None:
                description = ' ' + describe(self)
            return super().__str__() + description

    return _CustomExCard

# Factory for trigger extension events
def build_trigger_ex(location, *params, describe=None):
    class _CustomExTrigger(TriggerExtension):
        def __init__(self,
            player_turn,
            die_roll,
            required_roll,
            hard_to_block,
            easy_to_block,
            *args,
            **kwargs,
        ):
            super().__init__(
                location,
                player_turn,
                die_roll,
                required_roll,
                hard_to_block,
                easy_to_block,
            )
            populate(self, params, args, kwargs)

        def __str__(self):
            description = ''
            if describe is not None:
                description = ' ' + describe(self)
            return super().__str__() + description

    return _CustomExTrigger

# Message events
MsgStartGame      = build_msg('Start Game')

MsgEndGame        = build_msg('End Game')

MsgTraitPhase     = build_msg('Trait Phase')

MsgDrawPhase      = build_msg('Draw Phase')

MsgActionPhase    = build_msg('Action Phase')

MsgEndRound       = build_msg('End Round')

MsgScoringPhase   = build_msg('Scoring Phase')

MsgDiscardPhase   = build_msg('Discard Phase')

MsgStartRound     = build_msg('Start Round', 'game_round',
                              describe=lambda m: 'Round {}'
                                  .format(m.game_round))

MsgCardPlay       = build_msg('Card Play', 'actor_name', 'card_name', 'target_names',
                              describe=lambda m: '{} plays {} on {}'
                                  .format(m.actor_name, m.card_name, m.target_names))

MsgMove           = build_msg('Move', 'player_name', 'actor_name', 'start', 'end', 'start_facing', 'end_facing',
                              describe=lambda m: '{} moves {} from {} to {} (was facing {}, now {})'
                                  .format(m.player_name, m.actor_name, m.start, m.end, m.start_facing, m.end_facing))

MsgTriggerTerrain = build_msg('Trigger Terrain', 'actor_name', 'card_name', 'target', 'success', 'cause',
                              describe=lambda m: '{} {} {} square for {} ({})'
                                  .format(m.actor_name, ['failed to trigger', 'triggered'][m.success], m.card_name, m.target, m.cause))

MsgTriggerTrait   = build_msg('Trigger Trait', 'actor_name', 'card_name', 'target', 'success', 'cause',
                              describe=lambda m: '{} {} {} trait for {} ({})'
                                  .format(m.actor_name, ['failed to trigger', 'triggered'][m.success], m.card_name, m.target, m.cause))

MsgTriggerInHand  = build_msg('Trigger In Hand', 'actor_name', 'card_name', 'target', 'success', 'cause',
                              describe=lambda m: '{} {} {} in hand for {} ({})'
                                  .format(m.actor_name, ['failed to trigger', 'triggered'][m.success], m.card_name, m.target, m.cause))

MsgMustDiscard    = build_msg('Must Discard', 'group_name',
                              describe=lambda m: '{} must discard'
                                  .format(m.group_name))

MsgDiscard        = build_msg('Discard', 'group_name', 'card_name',
                              describe=lambda m: '{} discarded {}'
                                  .format(m.group_name, m.card_name))

MsgMustSelect     = build_msg('Must Select', 'player_name', 'option_names',
                              describe=lambda m: '{} must select a card from {}'
                                  .format(m.player_name, m.option_names))

MsgSelect         = build_msg('Select', 'player_name', 'card_name',
                              describe=lambda m: '{} selected {}'
                                  .format(m.player_name, m.card_name))

MsgMustTarget     = build_msg('Must Target', 'player_name',
                              describe=lambda m: '{} must select target'
                                  .format(m.player_name))

MsgMustTrait      = build_msg('Must Trait', 'player_name',
                              describe=lambda m: '{} must play a trait'
                                  .format(m.player_name))

MsgAttachTrait    = build_msg('Attach Trait', 'actor_name', 'card_name',
                              describe=lambda m: '{} attached to {}'
                                  .format(m.card_name, m.actor_name))

MsgDetachTrait    = build_msg('Detach Trait', 'actor_name', 'card_name',
                              describe=lambda m: '{} detached from {}'
                                  .format(m.card_name, m.actor_name))

MsgAttachTerrain  = build_msg('Attach Terrain', 'square', 'card_name',
                              describe=lambda m: '{} attached to {}'
                                  .format(m.card_name, m.square))

MsgDetachTerrain  = build_msg('Detach Terrain', 'square', 'card_name',
                              describe=lambda m: '{} detached from {}'
                                  .format(m.card_name, m.square))

MsgStartTimer     = build_msg('Start Timer', 'player_index', 'remaining',
                              describe=lambda m: 'Timer {} ({})'
                                  .format(m.player_index, display_seconds(m.remaining)))

MsgPauseTimer     = build_msg('Pause Timer', 'player_index', 'remaining',
                              describe=lambda m: 'Timer {} ({})'
                                  .format(m.player_index, display_seconds(m.remaining)))

MsgDefeat         = build_msg('Defeat', 'player_name',
                              describe=lambda m: '{} defeated'
                                  .format(m.player_name))

MsgCardDraw       = build_msg('Card Draw', 'player_name', 'group_name', 'card_name',
                              describe=lambda m: '{} drew {} for {}'
                                  .format(m.player_name, m.card_name, m.group_name))

MsgHiddenDraw     = build_msg('Hidden Draw', 'player_name', 'group_name',
                              describe=lambda m: '{} drew for {}'
                                  .format(m.player_name, m.group_name))

MsgReshuffle      = build_msg('Reshuffle', 'group_name', 'num_cards',
                              describe=lambda m: '{} shuffled {} cards into draw deck'
                                  .format(m.group_name, m.num_cards))

MsgFailedDraw     = build_msg('Failed Draw', 'group_name',
                              describe=lambda m: '{} failed to draw a card (empty draw deck)'
                                  .format(m.group_name))

MsgPlayerTurn     = build_msg('Player Turn', 'player_name',
                              describe=lambda m: '{} is now active'
                                  .format(m.player_name))

MsgPass           = build_msg('Pass', 'player_name',
                              describe=lambda m: '{} passed'
                                  .format(m.player_name))

MsgDamage         = build_msg('Damage', 'actor_name', 'hp',
                              describe=lambda m: '{} took {} damage'
                                  .format(m.actor_name, m.hp))

MsgHeal           = build_msg('Heal', 'actor_name', 'hp',
                              describe=lambda m: '{} healed {} hp'
                                  .format(m.actor_name, m.hp))

MsgDeath          = build_msg('Death', 'actor_name',
                              describe=lambda m: '{} died'
                                  .format(m.actor_name))

MsgBlock          = build_msg('Block', 'player_index', 'group_index', 'actor_index', 'card_name',
                              describe=lambda m: 'Actor {} of group {} of player {}) blocked {}'
                                  .format(m.actor_index, m.group_index, m.player_index, m.card_name))

MsgHealth         = build_msg('Health', 'player_index', 'group_index', 'actor_index', 'hp',
                              describe=lambda m: 'Actor {} of group {} of player {} has {} hp'
                                  .format(m.actor_index, m.group_index, m.player_index, m.hp))

MsgAutoselect     = build_msg('Autoselect', 'card_name',
                              describe=lambda m: 'Autoselected {}'
                                  .format(m.card_name))

MsgStopCard       = build_msg('Stop Card', 'card_name',
                              describe=lambda m: '{} was stopped'
                                  .format(m.card_name))

MsgCancelAction   = build_msg('Cancel Action', 'card_name',
                              describe=lambda m: 'Action {} was cancelled'
                                  .format(m.card_name))

# Extension events
ExSelectTarget   = build_ex('Select Target', 'target_player_indices', 'target_group_indices',
                            describe=lambda m: 'Selected groups {} of players {}'
                                .format(m.target_group_indices, m.target_player_indices))

ExSelectSquare   = build_ex('Select Square', 'square', 'facing',
                            describe=lambda m: 'Selected square {} with facing {}'
                                .format(m.square, m.facing))

ExRNG            = build_ex('RNG', 'rands',
                            describe=lambda m: 'Result: {}'
                                .format(m.rands))

ExMustTrait      = build_ex('Must Play Trait', 'player_index',
                            describe=lambda m: 'Player {} must play trait'
                                .format(m.player_index))

ExNoTraits       = build_ex('No Traits')

ExMustDiscard    = build_ex('Must Discard', 'player_index', 'group_index',
                            describe=lambda m: 'Group {} of player {} must discard'
                                .format(m.group_index, m.player_index))

ExNoDiscards     = build_ex('No Discards')

ExPass           = build_ex('Pass')

ExResign         = build_ex('Resign')

ExHandPeek       = build_ex('Hand Peek')

ExDeckPeek       = build_ex('Deck Peek')

ExRespawn        = build_ex('Respawn', 'player_indices', 'group_indices', 'actor_indices', 'squares', 'facings',
                            describe=lambda m: 'Actors {} from groups {} of players {} respawned at {}, facing {}'
                                .format(m.actor_indices, m.group_indices, m.player_indices, squares, facings))

ExStartTimer     = build_ex('Start Timer', 'player_index', 'remaining',
                            describe=lambda m: 'Timer {} ({})'
                                .format(m.player_index, display_seconds(m.remaining)))

ExPauseTimer     = build_ex('Pause Timer', 'player_index', 'remaining',
                            describe=lambda m: 'Timer {} ({})'
                                .format(m.player_index, display_seconds(m.remaining)))

ExCardPlay       = build_card_ex('Play')

ExCardDraw       = build_card_ex('Draw')

ExCardReveal     = build_card_ex('Reveal')

ExCardDiscard    = build_card_ex('Discard')

ExTriggerInHand  = build_trigger_ex('In Hand', 'player_index', 'group_index', 'card_index',
                                    describe=lambda m: 'card {} of group {} of player {}'
                                        .format(m.card_index, m.group_index, m.player_index))

ExTriggerTrait   = build_trigger_ex('Trait', 'player_index', 'group_index',
                                    describe=lambda m: 'card attached to group {} of player {}'
                                        .format(m.group_index, m.player_index))

ExTriggerTerrain = build_trigger_ex('Terrain', 'square',
                                    describe=lambda m: 'square {}'
                                        .format(m.square))
