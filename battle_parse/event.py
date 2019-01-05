# Logged battle events


# Helper function to display time
def display_seconds(sec):
    s = sec % 60
    m = sec // 60
    h, m = divmod(m, 60)
    return '{:02}:{:02}:{:02}'.format(h, m, s)

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
                description = ' ' + describe(m=self)
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
                description = ' ' + describe(e=self)
            return super().__str__() + description
    
    return _ExCustom

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
                description = ' ' + describe(e=self)
            return super().__str__() + description

    return _CustomExTrigger

# Message events
MsgStartGame = build_msg('Start Game')

MsgEndGame = build_msg('End Game')

MsgTraitPhase = build_msg('Trait Phase')

MsgDrawPhase = build_msg('Draw Phase')

MsgActionPhase = build_msg('Action Phase')

MsgEndRound = build_msg('End Round')

MsgScoringPhase = build_msg('Scoring Phase')

MsgDiscardPhase = build_msg('Discard Phase')

MsgStartRound = build_msg('Start Round',
    'game_round',
    describe='Round {m.game_round}'.format,
)

MsgCardPlay = build_msg('Card Play',
    'actor_name',
    'card_type',
    'target_names',
    describe='{m.actor_name} plays {m.card_type} on {m.target_names}'.format,
)

MsgMove = build_msg('Move',
    'player_name',
    'actor_name',
    'start',
    'end',
    'start_facing',
    'end_facing',
    describe='{m.player_name} moves {m.actor_name} from {m.start} to {m.end} (was facing {m.start_facing}, now {m.end_facing})'.format,
)

MsgTriggerTerrain = build_msg('Trigger Terrain',
    'actor_name',
    'card_type',
    'target',
    'success',
    'cause',
    describe=lambda m: '{m.actor_name} {0} {m.card_type} square for {m.target} ({m.cause})'.format(
        ['failed to trigger', 'triggered'][m.success], m=m,
    ),
)

MsgTriggerTrait = build_msg('Trigger Trait',
    'actor_name',
    'card_type',
    'target',
    'success',
    'cause',
    describe=lambda m: '{m.actor_name} {0} {m.card_type} trait for {m.target} ({m.cause})'.format(
        ['failed to trigger', 'triggered'][m.success], m=m,
    ),
)

MsgTriggerInHand = build_msg('Trigger In Hand',
    'actor_name',
    'card_type',
    'target',
    'success',
    'cause',
    describe=lambda m: '{m.actor_name} {0} {m.card_type} trait for {m.target} ({m.cause})'.format(
        ['failed to trigger', 'triggered'][m.success], m=m,
    ),
)

MsgMustDiscard = build_msg('Must Discard',
    'group_name',
    describe='{m.group_name} must discard'.format,
)

MsgDiscard = build_msg('Discard',
    'group_name',
    'card_type',
    describe='{m.group_name} discarded {m.card_type}'.format,
)

MsgMustSelect = build_msg('Must Select',
    'player_name',
    'option_names',
    describe='{m.player_name} must select a card from {m.option_names}'.format,
)

MsgSelect = build_msg('Select',
    'player_name',
    'card_type',
    describe='{m.player_name} selected {m.card_type}'.format,
)

MsgMustTarget = build_msg('Must Target',
    'player_name',
    describe='{m.player_name} must select target'.format,
)

MsgMustTrait = build_msg('Must Trait',
    'player_name',
    describe='{m.player_name} must play a trait'.format,
)

MsgAttachTrait = build_msg('Attach Trait',
    'actor_name',
    'card_type',
    describe='{m.card_type} attached to {m.actor_name}'.format,
)

MsgDetachTrait = build_msg('Detach Trait',
    'actor_name',
    'card_type',
    describe='{m.card_type} detached from {m.actor_name}'.format,
)

MsgAttachTerrain = build_msg('Attach Terrain',
    'square',
    'card_type',
    describe='{m.card_type} attached to {m.square}'.format,
)

MsgDetachTerrain = build_msg('Detach Terrain',
    'square',
    'card_type',
    describe='{m.card_type} detached from {m.square}'.format,
)

MsgStartTimer = build_msg('Start Timer',
    'player_index',
    'remaining',
    describe=lambda m: 'Timer {m.player_index} ({0})'.format(
        display_seconds(m.remaining), m=m,
    ),
)

MsgPauseTimer = build_msg('Pause Timer',
    'player_index',
    'remaining',
    describe=lambda m: 'Timer {m.player_index} ({0})'.format(
        display_seconds(m.remaining), m=m,
    ),
)

MsgDefeat = build_msg('Defeat',
    'player_name',
    describe='{m.player_name} defeated'.format,
)

MsgCardDraw = build_msg('Card Draw',
    'player_name',
    'group_name',
    'card_type',
    describe='{m.player_name} drew {m.card_type} for {m.group_name}'.format,
)

MsgHiddenDraw = build_msg('Hidden Draw',
    'player_name',
    'group_name',
    describe='{m.player_name} drew for {m.group_name}'.format,
)

MsgReshuffle = build_msg('Reshuffle',
    'group_name',
    'num_cards',
    describe='{m.group_name} shuffled {m.num_cards} cards into draw deck'.format,
)

MsgFailedDraw = build_msg('Failed Draw',
    'group_name',
    describe='{m.group_name} failed to draw a card (empty draw deck)'.format,
)

MsgPlayerTurn = build_msg('Player Turn',
    'player_name',
    describe='{m.player_name} is now active'.format,
)

MsgPass = build_msg('Pass',
    'player_name',
    describe='{m.player_name} passed'.format,
)

MsgDamage = build_msg('Damage',
    'actor_name',
    'hp',
    describe='{m.actor_name} took {m.hp} damage'.format,
)

MsgHeal = build_msg('Heal',
    'actor_name',
    'hp',
    describe='{m.actor_name} healed {m.hp} hp'.format,
)

MsgDeath = build_msg('Death',
    'actor_name',
    describe='{m.actor_name} died'.format,
)

MsgBlock = build_msg('Block',
    'player_index',
    'group_index',
    'actor_index',
    'card_type',
    describe='Actor {m.actor_index} of group {m.group_index} of player {m.player_index}) blocked {m.card_type}'.format,
)

MsgHealth = build_msg('Health',
    'player_index',
    'group_index',
    'actor_index',
    'hp',
    describe='Actor {m.actor_index} of group {m.group_index} of player {m.player_index} has {m.hp} hp'.format,
)

MsgAutoselect = build_msg('Autoselect',
    'card_type',
    describe='Autoselected {m.card_type}'.format,
)

MsgStopCard = build_msg('Stop Card',
    'card_type',
    describe='{m.card_type} was stopped'.format,
)

MsgCancelAction = build_msg('Cancel Action',
    'card_type',
    describe='Action {m.card_type} was cancelled'.format,
)

# Extension events
ExSelectTarget = build_ex('Select Target',
    'target_player_indices',
    'target_group_indices',
    'target_actor_indices',
    describe='Selected actors {e.target_actor_indices} of groups {e.target_group_indices} of players {e.target_player_indices}'.format,
)

ExSelectSquare = build_ex('Select Square',
    'square',
    'facing',
    describe='Selected square {e.square} with facing {e.facing}'.format,
)

ExRNG = build_ex('RNG',
    'rands',
    describe='Result: {e.rands}'.format,
)

ExMustTrait = build_ex('Must Play Trait',
    'player_index',
    describe='Player {e.player_index} must play trait'.format,
)

ExNoTraits = build_ex('No Traits')

ExMustDiscard = build_ex('Must Discard',
    'player_index',
    'group_index',
    describe='Group {e.group_index} of player {e.player_index} must discard'.format,
)

ExNoDiscards = build_ex('No Discards')

ExPass = build_ex('Pass')

ExResign = build_ex('Resign')

ExHandPeek = build_ex('Hand Peek')

ExDeckPeek = build_ex('Deck Peek')

ExRespawn = build_ex('Respawn',
    'player_indices',
    'group_indices',
    'actor_indices',
    'squares',
    'facings',
    describe='Actors {e.actor_indices} of groups {e.group_indices} of players {e.player_indices} respawned at {e.squares}, facing {e.facings}'.format,
)

ExStartTimer = build_ex('Start Timer',
    'player_index',
    'remaining',
    describe=lambda e: 'Timer {e.player_index} ({0})'.format(
        display_seconds(e.remaining), e=e,
    ),
)

ExPauseTimer = build_ex('Pause Timer',
    'player_index',
    'remaining',
    describe=lambda e: 'Timer {e.player_index} ({0})'.format(
        display_seconds(e.remaining), e=e,
    ),
)

ExCardReveal = build_ex('Card Reveal',
    'player_index',
    'group_index',
    'card_index',
    'original_player_index',
    'original_group_index',
    'card_type',
    'origin',
    describe='{e.card_type} from {e.origin}'.format,
)

ExCardPlay = build_ex('Card Play',
    'player_index',
    'group_index',
    'card_index',
    'original_player_index',
    'original_group_index',
    describe='Card {e.card_index} of group {e.group_index} of player {e.player_index}'.format,
)

ExCardDraw = build_ex('Card Draw',
    'player_index',
    'group_index',
    'card_index',
    'original_player_index',
    'original_group_index',
    describe='Card {e.card_index} of group {e.group_index} of player {e.player_index}'.format,
)

ExCardDiscard = build_ex('Card Discard',
    'player_index',
    'group_index',
    'card_index',
    'original_player_index',
    'original_group_index',
    describe='Card {e.card_index} of group {e.group_index} of player {e.player_index}'.format,
)

ExTriggerInHand = build_trigger_ex('In Hand',
    'player_index',
    'group_index',
    'card_index',
    describe='card {e.card_index} of group {e.group_index} of player {e.player_index}'.format,
)

ExTriggerTrait = build_trigger_ex('Trait',
    'player_index',
    'group_index',
    describe='card attached to group {e.group_index} of player {e.player_index}'.format,
)

ExTriggerTerrain = build_trigger_ex('Terrain',
    'square',
    describe='square {e.square}'.format,
)
