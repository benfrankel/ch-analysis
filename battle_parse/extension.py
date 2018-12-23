# Verbose battle log extension events


# Helper function
def display_seconds(sec):
    s = sec % 60
    m = sec // 60
    h, m = divmod(m, 60)
    return '{:02}:{:02}:{:02}'.format(h, m, s)


# Superclass for all extension events
class Extension:
    def __init__(self, name, player_turn):
        self.name = name
        self.player_turn = player_turn

    def __str__(self):
        if self.player_turn == -1:
            return 'The Game: {}'.format(self.name)
        else:
            return 'Player {}: {}'.format(self.player_turn, self.name)


# Superclass for card events
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
        return super().__str__() + ' [{} from {}]'.format(self.card_name, self.item_name)


# A card is played
class ExCardPlay(CardExtension):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Play', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# A card is drawn
class ExCardDraw(CardExtension):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Draw', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# A hidden card is drawn
class ExHiddenDraw(Extension):
    def __init__(self, player_turn):
        super().__init__('Hidden Draw', player_turn)

    def __str__(self):
        return super().__str__()


# A card is revealed
class ExCardReveal(CardExtension):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Reveal', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# A card is discarded
class ExCardDiscard(CardExtension):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Discard', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# Superclass for trigger events
class TriggerExtension(Extension):
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
class ExTriggerHand(TriggerExtension):
    def __init__(self, player_turn, die_roll, required_roll, hard_to_block, easy_to_block, player_index,
                 group_index, card_index):
        super().__init__('Hand', player_turn, die_roll, required_roll, hard_to_block, easy_to_block)
        self.player_index = player_index
        self.group_index = group_index
        self.card_index = card_index

    def __str__(self):
        return super().__str__()


# Trigger event where the card is an attachment
class ExTriggerAttachment(TriggerExtension):
    def __init__(self, player_turn, die_roll, required_roll, hard_to_block, easy_to_block, player_index, group_index):
        super().__init__('Attachment', player_turn, die_roll, required_roll, hard_to_block, easy_to_block)
        self.player_index = player_index
        self.group_index = group_index


# Trigger event where the card is a terrain attachment
class ExTriggerTerrain(TriggerExtension):
    def __init__(self, player_turn, die_roll, required_roll, hard_to_block, easy_to_block, x, y):
        super().__init__('Terrain', player_turn, die_roll, required_roll, hard_to_block, easy_to_block)
        self.x = x
        self.y = y

    def __str__(self):
        return super().__str__()


# A target selection event such as for a step attack
class ExSelectTarget(Extension):
    def __init__(self, player_turn, target_player_indices, target_group_indices):
        super().__init__('Select Target', player_turn)
        self.target_player_indices = target_player_indices
        self.target_group_indices = target_group_indices

    def __str__(self):
        return super().__str__()


# A square selection event such as for movement
class ExSelectSquare(Extension):
    def __init__(self, player_turn, x, y, fx, fy):
        super().__init__('Select Square', player_turn)
        self.x = x
        self.y = y
        self.fx = fx
        self.fy = fy

    def __str__(self):
        return super().__str__() + ' [{}, {}]'.format(self.x, self.y)


# Random numbers are generated
class ExRNG(Extension):
    def __init__(self, player_turn, rands):
        super().__init__('RNG', player_turn)
        self.rands = rands

    def __str__(self):
        return super().__str__()


# A group must play a trait
class ExMustTrait(Extension):
    def __init__(self, player_turn, player_index):
        super().__init__('Must Trait', player_turn)
        self.player_index = player_index

    def __str__(self):
        return super().__str__()


# No traits must be played
class ExNoTraits(Extension):
    def __init__(self, player_turn):
        super().__init__('No Traits', player_turn)

    def __str__(self):
        return super().__str__()


# A group must discard
class ExMustDiscard(Extension):
    def __init__(self, player_turn, player_index, group_index):
        super().__init__('Must Discard', player_turn)
        self.player_index = player_index
        self.group_index = group_index

    def __str__(self):
        return super().__str__()

# No cards must be discarded
class ExNoDiscards(Extension):
    def __init__(self, player_turn):
        super().__init__('No Discards', player_turn)

    def __str__(self):
        return super().__str__()


# Player passes their turn
class ExPass(Extension):
    def __init__(self, player_turn):
        super().__init__('Pass', player_turn)

    def __str__(self):
        return super().__str__()


# Player resigns
class ExResign(Extension):
    def __init__(self, player_turn):
        super().__init__('Resign', player_turn)

    def __str__(self):
        return super().__str__()


# Player peeks at card in their hand
class ExHandPeek(Extension):
    def __init__(self, player_turn):
        super().__init__('Hand Peek', player_turn)

    def __str__(self):
        return super().__str__()


# Player peeks at card in their deck
class ExDeckPeek(Extension):
    def __init__(self, player_turn):
        super().__init__('Deck Peek', player_turn)

    def __str__(self):
        return super().__str__()


# The time of an action is recorded
class ExTimer(Extension):
    def __init__(self, player_turn, player_index, start, remaining):
        super().__init__('Timer', player_turn)
        self.player_index = player_index
        self.start = start
        self.remaining = remaining

    def __str__(self):
        return super().__str__() + ' [{}]'.format(display_seconds(self.remaining))
