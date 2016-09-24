import gamedata


class Card:  # TODO: Card should know if it's attached to a character or to a tile.
    def __init__(self):
        self.card_type = None
        self.name = ''
        self.location = 0  # 0 = Draw, 1 = Hand, 2 = Discard

    def set(self, card_type):
        self.card_type = card_type
        self.name = card_type.name

    def reveal(self):
        self.location = 1

    def discard(self):
        self.location = 2

    def reshuffle(self):
        self.location = 0

    def is_known(self):
        return self.card_type is not None

    def in_draw(self):
        return self.location == 0

    def in_hand(self):
        return self.location == 1

    def in_discard(self):
        return self.location == 2

    def __eq__(self, other):
        return self.card_type == other.card_type

    def __str__(self):
        return self.name if self.name else '?'


class Item:
    def __init__(self, slot_type):
        self.item_type = None
        self.name = ''
        self.slot_type = slot_type
        if slot_type in ('Weapon', 'Divine Weapon', 'Staff'):
            self.cards = [Card() for _ in range(6)]
        else:
            self.cards = [Card() for _ in range(3)]

    def set(self, item_type):
        self.item_type = item_type
        self.name = item_type.name
        self.slot_type = item_type.slot_type
        for active_card, card in zip(self.cards, item_type.cards):
            active_card.set(card)

    def reshuffle(self):
        for card in self.cards:
            card.reshuffle()

    def is_known(self):
        return self.item_type is not None

    def __contains__(self, card_type):
        for card in self.cards:
            if card.card_type == card_type:
                return True
        return False

    def __eq__(self, other):
        return self.item_type == other.item_type

    def __str__(self):
        return self.name if self.name else '?'


class ItemSlot:
    def __init__(self, name):
        self.name = name
        self.item = Item(name)

    def set_item(self, item_type):
        if item_type.slot_type == self.name:
            self.item.set(item_type)
        else:
            raise ValueError("Cannot place " + item_type.name + " (" + item_type.slot_type + ") in " + self.name + " slot.")

    def remove_item(self):
        self.item = Item(self.name)

    def is_empty(self):
        return not self.item.is_known()

    def __contains__(self, item_type):
        return self.item.item_type == item_type

    def __str__(self):
        return str(self.item)


class ItemFrame:
    def __init__(self, archetype):
        self.name = archetype.name
        self.slot_types = archetype.slot_types
        self.slots = [ItemSlot(slot_type) for slot_type in archetype.slot_types]

    def add_item(self, item_type):
        for slot in self.slots:
            if item_type.slot_type == slot.name and slot.is_empty():
                slot.item.set(item_type)
                return
        raise ValueError("Cannot add " + item_type.name + " (" + item_type.slot_type + ") to " + self.name + " Frame without such a slot open.")

    def get_cards(self):
        return [card for slot in self.slots for card in slot.item.cards]

    def __contains__(self, item_type):
        return any(item_type in slot for slot in self.slots)

    def __str__(self):
        return ', '.join(str(slot) for slot in self.slots)


# Simultaneous reveal and discard (like parry or cloth armor proc) = play, functionally. (check log for triggerSucceed)
# What if a character plays an already revealed card (from hand)? (log will determine this)
# What if a character discards an already revealed card (from hand)? (log will determine this)
# What if a character dies?


class Character:  # TODO: Add Hand and proper functions to match log input.
    def __init__(self):
        self.name = ''
        self.figure = ''
        self.alive = True
        self.archetype = None
        self.item_frame = None
        self.deck = [Card() for _ in range(36)]

    def is_described(self):
        return self.name and self.figure and self.archetype is not None and self.item_frame is not None

    def set_archetype(self, name):
        self.archetype = gamedata.get_archetype(name)
        self.item_frame = ItemFrame(self.archetype)

    def get_hand(self):
        result = []
        for card in self.deck:
            if card.in_hand():
                result.append(card)
        return sorted(result, key=lambda x: x.name)

    def get_draw_deck(self):
        result = []
        for card in self.deck:
            if card.in_draw():
                result.append(card)
        return sorted(result, key=lambda x: x.name)

    def get_discard_deck(self):
        result = []
        for card in self.deck:
            if not card.in_draw():
                result.append(card)
        return sorted(result, key=lambda x: x.name)

    def update_deck_from_new_item(self, item_type, revealing_card_type):
        for card_type in item_type.cards:
            for card in self.deck:
                if not card.is_known() and card.in_draw():
                    card.set(card_type)
                    break
        for card in self.deck:
            if card.card_type == revealing_card_type and not card.in_discard():
                card.discard()
                break

    def reveal_card(self, card_type, item_type):
        if item_type in self.item_frame:
            for slot in self.item_frame.slots:
                if item_type in slot:
                    for active_card in slot.item.cards:
                        if active_card.card_type == card_type and active_card.in_draw():
                            active_card.reveal()
                            return active_card
        self.item_frame.add_item(item_type)
        self.update_deck_from_new_item(item_type, card_type)
        for slot in self.item_frame.slots:
            if item_type in slot:
                for active_card in slot.item.cards:
                    if active_card.card_type == card_type and active_card.in_draw():
                        active_card.reveal()
                        return active_card

    def play_card(self, card_type, item_type):
        active_card = self.reveal_card(card_type, item_type)
        active_card.discard()
        return active_card

    def discard_card(self, card_type):
        for card in self.deck:
            if card.card_type == card_type and not card.in_discard():
                card.discard()
                return card
        for card in self.deck:
            if not card.is_known():
                card.set(card_type)
                card.discard()
                return card

    def reshuffle(self):
        for slot in self.item_frame.slots:
            slot.item.reshuffle()

    def __str__(self):
        result = self.name + ' (' + self.archetype.race + ' ' + self.archetype.role + '):\n'
        result += 'Equipment: ' + str(self.item_frame) + '\n'
        result += 'Hand: ' + ', '.join(str(c) for c in self.get_hand()) + '\n'
        result += 'Draw Deck: ' + ', '.join(str(c) for c in self.get_draw_deck()) + '\n'
        result += 'Discard Deck: ' + ', '.join(str(c) for c in self.get_discard_deck())
        return result

    def __repr__(self):
        return str(self)


class Player:
    def __init__(self):
        self.name = ''
        self.index = -1
        self.rating = -1
        self.team = [Character() for _ in range(3)]

    def is_described(self):
        return self.name and self.index != -1 and self.rating != -1 and all([c.is_described() for c in self.team])


class Battle:
    def __init__(self):
        self.room_name = ''
        self.scenario_name = ''
        self.scenario_display_name = ''
        self.players = [Player() for _ in range(2)]
        self.enemy_index = -1

    def enemies(self):
        return self.players[self.enemy_index].team

    def is_described(self):
        return self.room_name and self.scenario_name and self.scenario_display_name and \
               all([p.is_described() for p in self.players]) and self.enemy_index != -1


