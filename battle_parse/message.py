# Battle log message events


# Helper function to display time
def display_seconds(sec):
    s = sec % 60
    m = sec // 60
    h, m = divmod(m, 60)
    return '{:02}:{:02}:{:02}'.format(h, m, s)

# Superclass for message events
class Message:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '[{}]'.format(self.name)

# Factory for message events
def build_msg(name, *params, describe=None):
    class _MsgCustom(Message):
        def __init__(self, *args):
            super().__init__(name)
            if len(params) != len(args):
                raise TypeError('Expected {} arguments ({} given)'.format(len(params), len(args)))
            for param, arg in zip(params, args):
                setattr(self, param, arg)

        def __str__(self):
            description = ''
            if describe is not None:
                description = ' ' + describe(self)
            return super().__str__() + description

    return _MsgCustom

# Simple Messages
MsgStartGame      = build_msg('Start Game')
MsgEndGame        = build_msg('End Game')
MsgTraitPhase     = build_msg('Trait Phase')
MsgDrawPhase      = build_msg('Draw Phase')
MsgActionPhase    = build_msg('Action Phase')
MsgEndRound       = build_msg('End Round')
MsgScoringPhase   = build_msg('Scoring Phase')
MsgDiscardPhase   = build_msg('Discard Phase')
MsgStartRound     = build_msg('Start Round', 'round',
                              describe=lambda m: '{}'.format(
                                  m.round))
MsgCardPlay       = build_msg('Card Play', 'group', 'card', 'targets',
                              describe=lambda m: '{} plays {} on {}'.format(
                                  m.group, m.card, m.targets))
MsgMove           = build_msg('Move', 'player', 'group', 'start', 'end', 'start_facing', 'end_facing',
                              describe=lambda m: '{} moves {} from {} to {} (was facing {}, now {})'.format(
                                  m.player, m.group, m.start, m.end, m.start_facing, m.end_facing))
MsgTriggerTerrain = build_msg('Trigger Terrain', 'group', 'card', 'target', 'success', 'cause',
                              describe=lambda m: '{} {} {} square for {} ({})'.format(
                                  m.group, ['failed to trigger', 'triggered'][m.success], m.card, m.target, m.cause))
MsgTriggerTrait   = build_msg('Trigger Trait', 'group', 'card', 'target', 'success', 'cause',
                              describe=lambda m: '{} {} {} trait for {} ({})'.format(
                                  m.group, ['failed to trigger', 'triggered'][m.success], m.card, m.target, m.cause))
MsgTriggerInHand  = build_msg('Trigger In Hand', 'group', 'card', 'target', 'success', 'cause',
                              describe=lambda m: '{} {} {} in hand for {} ({})'.format(
                                  m.group, ['failed to trigger', 'triggered'][m.success], m.card, m.target, m.cause))
MsgMustDiscard    = build_msg('Must Discard', 'group',
                              describe=lambda m:'{} must discard'.format(
                                  m.group))
MsgDiscard        = build_msg('Discard', 'group', 'card',
                              describe=lambda m:'{} discarded {}'.format(
                                  m.group, m.card))
MsgMustSelect     = build_msg('Must Select', 'player', 'options',
                              describe=lambda m:'{} must select a card from {}'.format(
                                  m.player, m.options))
MsgSelect         = build_msg('Select', 'player', 'card',
                              describe=lambda m:'{} selected {}'.format(
                                  m.player, m.card))
MsgMustTarget     = build_msg('Must Target', 'player',
                              describe=lambda m:'{} must select target'.format(
                                  m.player))
MsgMustTrait      = build_msg('Must Trait', 'player',
                              describe=lambda m:'{} must play a trait'.format(
                                  m.player))
MsgAttachTrait    = build_msg('Attach Trait', 'group', 'card',
                              describe=lambda m:'{} attached to {}'.format(
                                  m.card, m.group))
MsgDetachTrait    = build_msg('Detach Trait', 'group', 'card',
                              describe=lambda m:'{} detached from {}'.format(
                                  m.card, m.group))
MsgAttachTerrain  = build_msg('Attach Terrain', 'square', 'card',
                              describe=lambda m:'{} attached to {}'.format(
                                  m.card, m.square))
MsgDetachTerrain  = build_msg('Detach Terrain', 'square', 'card',
                              describe=lambda m:'{} detached from {}'.format(
                                  m.card, m.square))
MsgStartTimer     = build_msg('Start Timer', 'player_index', 'remaining',
                              describe=lambda m:'For player {} with {} remaining'.format(
                                  m.player_index, display_seconds(m.remaining)))
MsgStopTimer      = build_msg('Stop Timer', 'player_index', 'remaining',
                              describe=lambda m:'For player {} with {} remaining'.format(
                                  m.player_index, display_seconds(m.remaining)))
MsgDefeat         = build_msg('Defeat', 'player',
                              describe=lambda m:'{} defeated'.format(
                                  m.player))
MsgCardDraw       = build_msg('Card Draw', 'player', 'group', 'card',
                              describe=lambda m:'{} drew {} for {}'.format(
                                  m.player, m.card, m.group))
MsgHiddenDraw     = build_msg('Hidden Draw', 'player', 'group',
                              describe=lambda m:'{} drew for {}'.format(
                                  m.player, m.group))
MsgPlayerTurn     = build_msg('Player Turn', 'player',
                              describe=lambda m:'{} is now active'.format(
                                  m.player))
MsgPass           = build_msg('Pass', 'player',
                              describe=lambda m:'{} passed'.format(
                                  m.player))
MsgDamage         = build_msg('Damage', 'group', 'hp',
                              describe=lambda m:'{} took {} damage'.format(
                                  m.group, m.hp))
MsgHeal           = build_msg('Heal', 'group', 'hp',
                              describe=lambda m:'{} healed {} hp'.format(
                                  m.group, m.hp))
MsgDeath          = build_msg('Death', 'group',
                              describe=lambda m:'{} died'.format(
                                  m.group))
MsgBlock          = build_msg('Block', 'player_index', 'group_index', 'card',
                              describe=lambda m:'Group {} of player {} blocked {}'.format(
                                  m.group_index, m.player_index, m.card))
MsgHealth         = build_msg('Health', 'player_index', 'group_index', 'hp',
                              describe=lambda m:'Group {} of player {} has {} hp'.format(
                                  m.group_index, m.player_index, m.hp))
MsgAutoselect     = build_msg('Autoselect', 'card',
                              describe=lambda m:'Autoselected {}'.format(
                                  m.card))
MsgStopCard       = build_msg('Stop Card', 'card',
                              describe=lambda m:'{} was stopped'.format(
                                  m.card))
MsgCancelAction   = build_msg('Cancel Action', 'card',
                              describe=lambda m:'Action {} was cancelled'.format(
                                  m.card))
