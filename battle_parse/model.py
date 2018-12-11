import enum

import gamedata


class CardLocation(enum.Enum):
    Draw = 0
    Hand = 1
    Attached = 2
    Terrain = 3
    Discard = 4


# An instance of a card during a battle (type may be hidden)
class Card:
    def __init__(self, item=None):
        # Info
        self.name = '?'
        self.card_type = None

        # Index
        self.player_index = None if item is None else item.player_index
        self.group_index = None if item is None else item.group_index
        self.index = -1

        # Parents
        self.player = None if item is None else item.player
        self.group = None if item is None else item.group
        self.frame = None if item is None else item.frame
        self.slot = None if item is None else item.slot
        self.item = item
        self.item_name = None

        # State
        self.original_player_index = None if item is None else item.player_index
        self.original_group_index = None if item is None else item.group_index
        self.location = CardLocation.Draw
        self.x = -1
        self.y = -1

    def reveal(self, item, card_type):
        self.item = item
        self.card_type = card_type
        self.name = card_type.name

    def draw(self, card_index):
        self.index = card_index
        self.location = CardLocation.Hand

    # a la Battlefield Training
    def lend(self, player_index, group_index, card_index):
        self.player_index = player_index
        self.group_index = group_index
        self.index = card_index

    # a la Traveling Curse
    def travel(self, player_index, group_index):
        self.player_index = player_index
        self.group_index = group_index
        self.index = -1
        self.x = -1
        self.y = -1
        self.location = CardLocation.Draw

    def attach(self, player_index, group_index):
        self.player_index = player_index
        self.group_index = group_index
        self.index = -1
        self.x = -1
        self.y = -1

    def attach_terrain(self, x, y):
        self.player_index = -1
        self.group_index = -1
        self.index = -1
        self.x = x
        self.y = y

    def discard(self):
        self.player_index = self.original_player_index
        self.group_index = self.original_group_index
        self.index = -1
        self.x = -1
        self.y = -1
        self.location = CardLocation.Discard

    def reshuffle(self):
        if self.location == 4:
            self.location = CardLocation.Draw

    def is_hidden(self):
        return self.card_type is None

    def in_draw(self):
        return self.location == CardLocation.Draw

    def in_hand(self):
        return self.location == CardLocation.Hand

    def is_attached(self):
        return self.location == CardLocation.Attached

    def is_terrain(self):
        return self.location == CardLocation.Terrain

    def in_discard(self):
        return self.location == CardLocation.Discard

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# An instance of an item during a battle (type may be hidden)
class Item:
    def __init__(self, slot):
        # Info
        self.name = '?'
        self.item_type = None

        # Index
        self.player_index = slot.player_index
        self.group_index = slot.group_index

        # Parents
        self.player = slot.player
        self.group = slot.group
        self.frame = slot.frame
        self.slot = slot

        # Children
        if slot.name in ('Weapon', 'Divine Weapon', 'Staff'):
            self.cards = [Card(self) for _ in range(6)]
        else:
            self.cards = [Card(self) for _ in range(3)]

    def reveal(self, item_type):
        self.item_type = item_type
        self.name = item_type.name
        for card, card_type in zip(self.cards, item_type.cards):
            card.reveal(self, card_type)

    def reshuffle(self):
        for card in self.cards:
            card.reshuffle()

    def is_hidden(self):
        return self.item_type is None

    def __contains__(self, card_type):
        for card in self.cards:
            if card.card_type == card_type:
                return True
        return False

    def __eq__(self, other):
        return self.item_type == other.item_type

    def __str__(self):
        return '{} ({})'.format(self.name, self.slot.name)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# An instance of a slot type (e.g. Weapon, Staff, Divine Skill) that can contain an Item during a battle
class ItemSlot:
    def __init__(self, frame, name):
        # Info
        self.name = name

        # Index
        self.player_index = frame.player_index
        self.group_index = frame.group_index

        # Parents
        self.player = frame.player
        self.group = frame.group
        self.frame = frame

        # Children
        self.item = Item(self)

    def set_item_type(self, item_type):
        if item_type.slot_type != self.name:
            raise ValueError('Cannot place "{}" ({}) in {} slot'.format(item_type.name, item_type.slot_type, self.name))

        self.item.reveal(item_type)

    def remove_item(self):
        self.item = Item(self)

    def is_empty(self):
        return self.item.is_hidden()

    def __contains__(self, item_type):
        return self.item.item_type == item_type

    def __str__(self):
        return str(self.item)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# Models an instance of a character archetype's list of item slots during a battle
class ItemFrame:
    def __init__(self, group):
        # Info
        self.name = '?'
        self.archetype = None

        # Index
        self.player_index = group.player.index
        self.group_index = group.index

        # Parents
        self.player = group.player
        self.group = group

        # Children
        self.slot_types = []
        self.slots = []

    def set_archetype(self, archetype):
        self.archetype = archetype
        self.name = archetype.name
        self.slot_types = archetype.slot_types
        self.slots = [ItemSlot(self, slot_type) for slot_type in self.slot_types]

    def add_item(self, item_type):
        for slot in self.slots:
            if item_type.slot_type == slot.name and slot.is_empty():
                slot.item.reveal(item_type)
                return
        raise ValueError('Cannot add "{}" ({}) to {} Frame without such a slot open'.format(item_type.name, item_type.slot_type, self.name))

    def get_cards(self):
        return [card for slot in self.slots for card in slot.item.cards]

    def __contains__(self, item_type):
        return any(item_type in slot for slot in self.slots)

    def __str__(self):
        return ', '.join(str(slot) for slot in self.slots)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# An instance of an actor group during a battle (name, figure, archetype, item frame)
class Group:
    def __init__(self, player, index):
        # Info
        self.name = '?'
        self.figure = '?'
        self.archetype = None

        # Index
        self.player_index = player.index
        self.index = index

        # Parents
        self.player = player

        # Children
        self.item_frame = ItemFrame(self)
        self.draw_deck = []
        self.discard_deck = []
        self.hand = []

        # State
        self.alive = True
        self.must_draw = -1

    def is_described(self):
        return self.name != '?' and self.figure != '?'  and self.archetype is not None

    def set_archetype(self, archetype_name):
        archetype = gamedata.get_archetype(archetype_name)
        self.archetype = archetype
        self.item_frame.set_archetype(archetype)
        self.draw_deck = [card for slot in self.item_frame.slots for card in slot.item.cards]

    def reshuffle(self):
        for slot in self.item_frame.slots:
            slot.item.reshuffle()

    def reveal_card(self, event, from_deck=False):
        card_type = gamedata.get_card(event.card_name)

        if event.original_player_index == -1:
            card = Card()

            card.original_player_index = event.original_player_index
            card.original_group_index = event.original_group_index
            card.player_index = event.player_index
            card.group_index = event.group_index
            card.index = event.card_index

            card.reveal(None, card_type)

            self.hand.append(card)
            self.hand.sort(key=lambda x: x.index)
            return

        item_type = gamedata.get_item(event.item_name)

        if from_deck:
            # See if card has already been revealed in draw deck
            for card in self.draw_deck:
                if card.card_type == card_type and card.item.item_type == item_type:
                    return
            else:
                # Reveal item
                self.item_frame.add_item(item_type)

        elif self.hand[event.card_index].is_hidden():
            # Reveal item
            self.item_frame.add_item(item_type)

            # Card in hand should match reveal
            for i, back in enumerate(self.draw_deck):
                if back.card_type == card_type and back.item.item_type == item_type:
                    self.draw_deck[i] = self.hand[event.card_index]
                    self.hand[event.card_index] = back
                    break

            # Previously hidden cards in hand should remain hidden
            for i, card in enumerate(self.hand):
                if i == event.card_index:
                    continue

                if card.item is self.hand[event.card_index].item:
                    for j, back in enumerate(self.draw_deck):
                        if back.is_hidden():
                            self.draw_deck[j] = card
                            self.hand[i] = back

    def discard_card(self, event):  # TODO: DiscardToOpponent
        # If DiscardToOpponentComponent, wait for genRand to determine where to travel to
        # components = gamedata.get_card(event.card_name).components
        self.hand[event.card_index].discard()
        self.draw_deck.append(self.hand.pop(event.card_index))
        for card in self.hand[event.card_index:]:
            card.index -= 1

    def draw_card(self, event):
        card_type = gamedata.get_card(event.card_name)
        item_type = gamedata.get_item(event.item_name)

        for i, card in enumerate(self.draw_deck):
            if card.card_type == card_type and card.item.item_type == item_type:
                break
        else:
            raise Exception('Could not find card in draw deck:', event.card_name)

        card = self.draw_deck.pop(i)
        self.hand.append(card)
        self.hand.sort(key=lambda x: x.index)
        card.draw(event.card_index)

    def hidden_draw(self):  # TODO: Shamefully ugly method
        if self.must_draw == -1:
            self.must_draw = 5  # TODO: this is a hack
        elif self.must_draw == 0:
            self.must_draw = 2  # TODO: what about bless/unholy energy/etc.?
        for i, card in enumerate(self.draw_deck):
            if card.is_hidden():
                self.draw_deck.pop(i)
                self.hand.append(card)
                card.draw(len(self.hand))
                break
        self.must_draw -= 1
        if self.must_draw == 2:
            self.must_draw = 0  # TODO: Just burn this down and refactor the whole file
        return self.must_draw == 0

    def play_card(self, event):
        self.discard_card(event)
        pass  # TODO

    def __str__(self):
        return '{} ({} {})\nEquipment: {}'.format(self.name, self.archetype.race, self.archetype.role, self.item_frame)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# An instance of a player during a battle
class Player:
    def __init__(self, scenario, index):
        # Info
        self.name = '?'
        self.id = -1
        self.user_id = -1
        self.rating = -1

        # Index
        self.index = index

        # Parents
        self.scenario = scenario

        # Children
        self.groups = [Group(self, i) for i in range(3)]

        # State
        self.stars = 0
        self.drawing_group = 0

    def is_described(self):
        return self.name != '?' and self.rating != -1 and self.user_id != -1 and\
               all([c.is_described() for c in self.groups])

    def reveal_card(self, event, from_deck=False):
        self.groups[event.group_index].reveal_card(event, from_deck)

    def discard_card(self, event):  # TODO: DiscardToOpponent
        self.groups[event.group_index].discard_card(event)

    def draw_card(self, event):
        self.groups[event.group_index].draw_card(event)

    def hidden_draw(self):
        if self.groups[self.drawing_group].hidden_draw():
            self.drawing_group += 1
            self.drawing_group %= 3

    def play_card(self, event):
        self.groups[event.group_index].play_card(event)


# An instance of a map tile during a battle
class Square:
    def __init__(self, x, y, flip_x, flip_y, image_name, terrain):
        # Info
        self.name = image_name
        self.flip_x = flip_x
        self.flip_y = flip_y

        # Placement
        self.x = x
        self.y = y

        # State
        self.terrain = terrain


# An instance of a map doodad during a battle (static; doodads stay the same throughout the battle)
class Doodad:
    def __init__(self, x, y, flip_x, flip_y, image_name, marker):
        # Info
        self.name = image_name
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.marker = marker

        # Placement
        self.x = x
        self.y = y


# An instance of a map during a battle (bunch of tiles and doodads)
class Map:
    def __init__(self, scenario):
        # Info
        self.max_x = 0
        self.max_y = 0

        # Parents
        self.scenario = scenario

        # Children
        self.squares = dict()
        self.doodads = list()

    def is_described(self):
        return True  # TODO?

    def add_square(self, x, y, flip_x, flip_y, image_name, terrain):
        if x > self.max_x:
            self.max_x = x
        if y > self.max_y:
            self.max_y = y
        self.squares[x, y] = Square(x, y, flip_x, flip_y, image_name, terrain)

    def add_doodad(self, x, y, flip_x, flip_y, image_name, battle):
        self.doodads.append(Doodad(x, y, flip_x, flip_y, image_name, battle))

    def get_square(self, x, y):
        return self.squares[x, y]

    def __str__(self):
        square_char = {'Open': '.', 'Difficult': '-', 'Impassable': 'o', 'Blocked': '#', 'Victory': '@'}
        result = ''
        for x in range(self.max_x+1):
            if x != 0:
                result += '\n'
            for y in range(self.max_y+1):
                if (x, y) in self.squares:
                    result += square_char[self.squares[x, y].terrain]
                else:
                    result += ' '
        return result


# A scenario (map, players, characters, cards, items, etc.)
class Scenario:
    def __init__(self):
        # Info
        self.name = '?'
        self.display_name = '?'
        self.room_name = '?'

        # Children
        self.map = Map(self)
        self.players = [Player(self, i) for i in range(2)]
        self.user = None
        self.enemy = None

    def set_user(self, user_index):
        self.user = self.players[user_index]
        self.enemy = self.players[1 - user_index]

    def is_described(self):
        return self.name != '?' and self.display_name != '?' and self.room_name != '?' and self.enemy is not None and\
               self.map.is_described() and all(p.is_described() for p in self.players)

    def update(self, event):  # TODO
        try:
            print()
            print('Event:', event)
            print('Hand before:', self.players[event.player_index].groups[event.group_index].hand)
        except Exception:
            pass

        # TODO: Fix traits (Must Play Trait -> No More Traits)
        # TODO: In the interim, REPLACE cards played by enemy
        # TODO: What about cards drawn by user? How do you know what should be replaced by the new card?

        if event.name == 'Card Draw':
            self.players[event.player_index].reveal_card(event, from_deck=True)
            self.players[event.player_index].draw_card(event)
        elif event.name == 'Hidden Draw':
            self.enemy.hidden_draw()
        elif event.name == 'Card Reveal':
            self.players[event.player_index].reveal_card(event)
        elif event.name == 'Card Discard':
            self.players[event.player_index].reveal_card(event)
            self.players[event.player_index].discard_card(event)
        elif event.name == 'Card Play':
            self.players[event.player_index].reveal_card(event)
            self.players[event.player_index].play_card(event)
        elif event.name == 'Target':
            pass
        elif event.name == 'Square':
            pass
        elif event.name == 'Trigger Hand':
            pass
        elif event.name == 'Trigger Attachment':
            pass
        elif event.name == 'Trigger Terrain':
            pass
        elif event.name == 'Pass':
            pass

        try:
            print('Hand after:', self.players[event.player_index].groups[event.group_index].hand)
        except Exception:
            pass
