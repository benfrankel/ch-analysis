# Battle event objects


# Superclass for all events
class Event:
    def __init__(self, name, player_turn):
        self.name = name
        self.player_turn = player_turn

    def __str__(self):
        return 'Player {}: {}'.format(self.player_turn, self.name)


# Superclass for card events
class CardEvent(Event):
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
        return super().__str__() + ' [{} from {}]'.format(self.card_name, self.item_name)


# A card is played
class CardPlay(CardEvent):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Play', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# A card is drawn
class CardDraw(CardEvent):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Draw', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# A hidden card is drawn
class HiddenDraw(Event):
    def __init__(self, player_turn):
        super().__init__('Hidden Draw', player_turn)

    def __str__(self):
        return super().__str__()


# A card is revealed
class CardReveal(CardEvent):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Reveal', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# A card is discarded
class CardDiscard(CardEvent):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Discard', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# Superclass for trigger events
class TriggerEvent(Event):
    def __init__(self, name, player_turn, die_roll, required_roll, hard_to_block, easy_to_block):
        super().__init__('Trigger ' + name, player_turn)
        self.die_roll = die_roll
        self.required_roll = required_roll
        self.hard_to_block = hard_to_block
        self.easy_to_block = easy_to_block
        self.success = die_roll + easy_to_block - hard_to_block >= required_roll

    def __str__(self):
        return super().__str__() + ' [{}]'.format(['Fail', 'Success'][self.success])


# Trigger event where the card is in hand
class TriggerHand(TriggerEvent):
    def __init__(self, player_turn, die_roll, required_roll, hard_to_block, easy_to_block, player_index,
                 group_index, card_index):
        super().__init__('Hand', player_turn, die_roll, required_roll, hard_to_block, easy_to_block)
        self.player_index = player_index
        self.group_index = group_index
        self.card_index = card_index

    def __str__(self):
        return super().__str__()


# Trigger event where the card is an attachment
class TriggerAttachment(TriggerEvent):
    def __init__(self, player_turn, die_roll, required_roll, hard_to_block, easy_to_block, player_index, group_index):
        super().__init__('Attachment', player_turn, die_roll, required_roll, hard_to_block, easy_to_block)
        self.player_index = player_index
        self.group_index = group_index


# Trigger event where the card is a terrain attachment
class TriggerTerrain(TriggerEvent):
    def __init__(self, player_turn, die_roll, required_roll, hard_to_block, easy_to_block, x, y):
        super().__init__('Terrain', player_turn, die_roll, required_roll, hard_to_block, easy_to_block)
        self.x = x
        self.y = y

    def __str__(self):
        return super().__str__()


# A target selection event such as for a step attack
class SelectTarget(Event):
    def __init__(self, player_turn, target_player_indices, target_group_indices):
        super().__init__('Select Target', player_turn)
        self.target_player_indices = target_player_indices
        self.target_group_indices = target_group_indices

    def __str__(self):
        return super().__str__()


# A square selection event such as for movement
class SelectSquare(Event):
    def __init__(self, player_turn, x, y, fx, fy):
        super().__init__('Select Square', player_turn)
        self.x = x
        self.y = y
        self.fx = fx
        self.fy = fy

    def __str__(self):
        return super().__str__() + ' [{}, {}]'.format(self.x, self.y)


# Random numbers are generated
class RNG(Event):
    def __init__(self, player_turn, rands):
        super().__init__('RNG', player_turn)
        self.rands = rands

    def __str__(self):
        return super().__str__()


# A group must play a trait
class MustPlayTrait(Event):
    def __init__(self, player_turn, player_index):
        super().__init__('Must Play Trait', player_turn)
        self.player_index = player_index

    def __str__(self):
        return super().__str__()


# No traits must be played
class NoTraits(Event):
    def __init__(self, player_turn):
        super().__init__('No Traits', player_turn)

    def __str__(self):
        return super().__str__()


# A group must discard
class MustDiscard(Event):
    def __init__(self, player_turn, player_index, group_index):
        super().__init__('Must Discard', player_turn)
        self.player_index = player_index
        self.group_index = group_index

    def __str__(self):
        return super().__str__()

# No cards must be discarded
class NoDiscards(Event):
    def __init__(self, player_turn):
        super().__init__('No Discards', player_turn)

    def __str__(self):
        return super().__str__()


# Player passes their turn
class Pass(Event):
    def __init__(self, player_turn):
        super().__init__('Pass', player_turn)

    def __str__(self):
        return super().__str__()


# Player resigns
class Resign(Event):
    def __init__(self, player_turn):
        super().__init__('Resign', player_turn)

    def __str__(self):
        return super().__str__()


# Player peeks at card in their hand
class HandPeek(Event):
    def __init__(self, player_turn):
        super().__init__('Hand Peek', player_turn)

    def __str__(self):
        return super().__str__()


# Player peeks at card in their deck
class DeckPeek(Event):
    def __init__(self, player_turn):
        super().__init__('Deck Peek', player_turn)

    def __str__(self):
        return super().__str__()


# The time of an action is recorded
class Timer(Event):
    def __init__(self, player_turn, switch_player, remaining):
        super().__init__('Timer', player_turn)
        self.switch_player = switch_player
        self.remaining = remaining

    def __str__(self):
        h = self.remaining // 3600
        m = (self.remaining % 3600) // 60
        s = self.remaining % 60
        return super().__str__() + ' [{:02}:{:02}:{:02}]'.format(h, m, s)
