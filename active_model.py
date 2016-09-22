import model
import gamedata


class ActiveCard:
    def __init__(self):
        self.card_type = None
        self.name = ''
        self.pile = 0  # 0 = Draw, 1 = Hand, 2 = Discard

    def set(self, card_type):
        self.card_type = card_type
        self.name = card_type.name

    def reveal(self):
        self.pile = 1

    def discard(self):
        self.pile = 2

    def reshuffle(self):
        self.pile = 0

    def is_known(self):
        return self.card_type is not None

    def in_draw(self):
        return self.pile == 0

    def in_hand(self):
        return self.pile == 1

    def in_discard(self):
        return self.pile == 2

    def __eq__(self, other):
        return self.card_type == other.card_type

    def __str__(self):
        return self.name if self.name else '?'


class ActiveItem:
    def __init__(self, slot_type):
        self.item_type = None
        self.name = ''
        self.slot_type = slot_type
        if slot_type in ('Weapon', 'Divine Weapon', 'Staff'):
            self.cards = [ActiveCard() for _ in range(6)]
        else:
            self.cards = [ActiveCard() for _ in range(3)]

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


class Slot:
    def __init__(self, name):
        self.name = name
        self.item = ActiveItem(name)

    def set_item(self, item_type):
        if item_type.slot_type == self.name:
            self.item.set(item_type)
        else:
            raise ValueError("Cannot place " + item_type.name + " (" + item_type.slot_type + ") in " + self.name + " slot.")

    def remove_item(self):
        self.item = ActiveItem(self.name)

    def is_empty(self):
        return not self.item.is_known()

    def __contains__(self, item_type):
        return self.item.item_type == item_type

    def __str__(self):
        return str(self.item)


class Frame:
    def __init__(self, archetype):
        self.name = archetype.name
        self.slot_types = archetype.slot_types
        self.slots = [Slot(slot_type) for slot_type in archetype.slot_types]

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


# Simultaneous reveal and discard (like parry or cloth armor proc) = play, functionally.
# What if a character plays an already revealed card (from hand)?
# What if a character discards an already revealed card (from hand)?
# If a character dies, log all the discards if you want info on the deck and then stop tracking.


class ActiveCharacter:  # TODO: Add Hand and proper functions to match log input.
    def __init__(self):
        self.name = ''
        self.figure = ''
        self.alive = True
        self.archetype = None
        self.frame = None
        self.deck = [ActiveCard() for _ in range(36)]

    def set_archetype(self, name):
        self.archetype = gamedata.get_archetype(name)
        self.frame = Frame(self.archetype)

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
        if item_type in self.frame:
            for slot in self.frame.slots:
                if item_type in slot:
                    for active_card in slot.item.cards:
                        if active_card.card_type == card_type and active_card.in_draw():
                            active_card.reveal()
                            return active_card
        self.frame.add_item(item_type)
        self.update_deck_from_new_item(item_type, card_type)
        for slot in self.frame.slots:
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
        for slot in self.frame.slots:
            slot.item.reshuffle()

    def __str__(self):
        result = self.name + ' (' + self.archetype.race + ' ' + self.archetype.role + '):\n'
        result += 'Equipment: ' + str(self.frame) + '\n'
        result += 'Hand: ' + ', '.join(str(c) for c in self.get_hand()) + '\n'
        result += 'Draw Deck: ' + ', '.join(str(c) for c in self.get_draw_deck()) + '\n'
        result += 'Discard Deck: ' + ', '.join(str(c) for c in self.get_discard_deck())
        return result

    def __repr__(self):
        return str(self)


class ActiveBattle:
    def __init__(self):
        self.room_name = ''
        self.scenario_name = ''
        self.scenario_display_name = ''
        self.enemies = [ActiveCharacter() for _ in range(3)]
        self.enemy_index = -1
        self.enemy_name = ''

    def is_described(self):
        result = bool(self.room_name and self.scenario_name and self.scenario_display_name and self.enemy_name)
        result &= self.enemy_index != -1
        return result


