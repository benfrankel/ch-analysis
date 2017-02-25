import gamedata


# An instance of a card during a battle. Card type may be hidden.
class Card:
    def __init__(self, original_player_index, original_group_index, item_type=None, card_type=None):
        self.original_player_index = original_player_index
        self.original_group_index = original_group_index
        self.player_index = original_player_index
        self.group_index = original_group_index
        self.index = -1
        self.location = 0  # 0 = Draw, 1 = Hand, 2 = Attached, 3 = Terrain, 4 = Discard
        self.card_type = None
        self.name = ''
        if card_type is not None:
            self.name = card_type.name
        self.item_type = item_type
        self.item_name = ''
        if item_type is not None:
            self.item_name = item_type.name
        self.x = -1
        self.y = -1

    def reveal(self, item_type, card_type):
        self.card_type = card_type
        self.name = card_type.name
        self.item_type = item_type
        self.item_name = item_type.name

    def draw(self, card_index):
        self.index = card_index
        self.location = 1

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
        self.location = 0

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
        self.location = 4

    def reshuffle(self):
        if self.location == 4:
            self.location = 0

    def is_known(self):
        return self.card_type is not None

    def in_draw(self):
        return self.location == 0

    def in_hand(self):
        return self.location == 1

    def is_attached(self):
        return self.location == 2

    def is_terrain(self):
        return self.location == 3

    def in_discard(self):
        return self.location == 4

    def __str__(self):
        return self.name if self.name else '?'

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# An instance of an item during a battle. Item type may be hidden.
class Item:
    def __init__(self, player_index, group_index, slot_name):
        self.player_index = player_index
        self.group_index = group_index
        self.item_type = None
        self.name = ''
        self.slot_name = slot_name
        if slot_name in ('Weapon', 'Divine Weapon', 'Staff'):
            self.cards = [Card(player_index, group_index) for _ in range(6)]
        else:
            self.cards = [Card(player_index, group_index) for _ in range(3)]

    def reveal(self, item_type):
        self.item_type = item_type
        self.name = item_type.name
        self.slot_name = item_type.slot_type
        for card, card_type in zip(self.cards, item_type.cards):
            card.reveal(item_type, card_type)

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

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# An instance of a slot type (e.g. Weapon, Staff, Divine Skill) that can contain an Item during a battle.
class ItemSlot:
    def __init__(self, player_index, group_index, name):
        self.name = name
        self.player_index = player_index
        self.group_index = group_index
        self.item = Item(player_index, group_index, name)

    def set_item(self, item_type):
        if item_type.slot_type == self.name:
            self.item.reveal(item_type)
        else:
            raise ValueError("Cannot place " + item_type.name + " (" + item_type.slot_type + ") in " + self.name + " slot.")

    def remove_item(self):
        self.item = Item(self.player_index, self.group_index, self.name)

    def is_empty(self):
        return not self.item.is_known()

    def __contains__(self, item_type):
        return self.item.item_type == item_type

    def __str__(self):
        return str(self.item)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# Models an instance of a character archetype's list of item slots during a battle.
class ItemFrame:
    def __init__(self, player_index, group_index, archetype):
        self.player_index = player_index
        self.group_index = group_index
        self.archetype_name = archetype.name
        self.slot_types = archetype.slot_types
        self.slots = [ItemSlot(player_index, group_index, slot_type) for slot_type in archetype.slot_types]

    def add_item(self, item_type):
        for slot in self.slots:
            if item_type.slot_type == slot.name and slot.is_empty():
                slot.item.reveal(item_type)
                return
        raise ValueError("Cannot add " + item_type.name + " (" + item_type.slot_type + ") to " + self.archetype_name + " Frame without such a slot open.")

    def get_cards(self):
        return [card for slot in self.slots for card in slot.item.cards]

    def __contains__(self, item_type):
        return any(item_type in slot for slot in self.slots)

    def __str__(self):
        return ', '.join(str(slot) for slot in self.slots)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.archetype_name)


# An instance of an actor group during a battle (name, figure, archetype, item frame).
class Group:
    def __init__(self, player_index, index):
        self.player_index = player_index
        self.index = index
        self.name = ''
        self.figure = ''
        self.alive = True
        self.archetype = None
        self.item_frame = None

    def is_described(self):
        return self.name and self.figure and self.archetype is not None and self.item_frame is not None

    def set_archetype(self, archetype_name):
        self.archetype = gamedata.get_archetype(archetype_name)
        self.item_frame = ItemFrame(self.player_index, self.index, self.archetype)

    def reshuffle(self):
        for slot in self.item_frame.slots:
            slot.item.reshuffle()

    def __str__(self):
        result = self.name + ' (' + self.archetype.race + ' ' + self.archetype.role + '):\n'
        result += 'Equipment: ' + str(self.item_frame) + '\n'
        return result

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# An instance of a player during a battle.
class Player:
    def __init__(self, index):
        self.index = index
        self.name = ''
        self.id = -1
        self.user_id = -1
        self.rating = -1
        self.groups = [Group(index, i) for i in range(3)]

    def is_described(self):
        return self.name and self.rating != -1 and self.user_id != -1 and all([c.is_described() for c in self.groups])


# An instance of a map tile during a battle.
class Square:
    def __init__(self, x, y, flip_x, flip_y, image_name, terrain):
        self.x = x
        self.y = y
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.image_name = image_name
        self.terrain = terrain


# An instance of a map doodad during a battle (not dynamic; doodads stay the same throughout the battle).
class Doodad:
    def __init__(self, x, y, flip_x, flip_y, image_name, marker):
        self.x = x
        self.y = y
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.image_name = image_name
        self.marker = marker


# An instance of a map during a battle (bunch of tiles and doodads).
class Map:
    def __init__(self):
        self.squares = dict()
        self.doodads = list()
        self.max_x = 0
        self.max_y = 0

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
        result = ''
        for y in range(self.max_y+1):
            for x in range(self.max_x+1):
                if (x, y) in self.squares:
                    square = self.squares[x, y]
                    if square.terrain == 'Open':
                        result += '.'
                    elif square.terrain == 'Difficult':
                        result += '-'
                    elif square.terrain == 'Impassable':
                        result += 'o'
                    elif square.terrain == 'Blocked':
                        result += '#'
                    elif square.terrain == 'Victory':
                        result += '@'
                else:
                    result += ' '
            result += '\n'
        return result


# A battle (map, players, characters, cards, items, etc.)
class Battle:
    def __init__(self):
        self.map = Map()
        self.room_name = ''
        self.scenario_name = ''
        self.scenario_display_name = ''
        self.players = [Player(i) for i in range(2)]
        self.user = None
        self.enemy = None
        self.card_pool = [Card(p_index, g_index) for p_index in range(1) for g_index in range(3) for _ in range(36)]

    def set_user(self, user_index):
        self.user = self.players[user_index]
        self.enemy = self.players[1 - user_index]

    def is_described(self):
        return self.room_name and self.scenario_name and self.scenario_display_name and self.enemy is not None and\
               all([p.is_described() for p in self.players])

    def get_discard_deck(self, player_index, group_index):
        discard_deck = []
        for card in self.card_pool:
            if card.player_index == player_index and card.group_index == group_index and card.in_discard():
                discard_deck.append(card)
        return discard_deck

    def get_draw_deck(self, player_index, group_index):
        draw_deck = []
        for card in self.card_pool:
            if card.player_index == player_index and card.group_index == group_index and card.in_draw():
                draw_deck.append(card)
        return draw_deck

    def get_hand(self, player_index, group_index):
        hand = []
        for card in self.card_pool:
            if card.player_index == player_index and card.group_index == group_index and card.in_hand():
                hand.append(card)
        return sorted(hand, key=lambda x: x.card_index)

    def get_attachments(self, player_index, group_index):
        attachments = []
        for card in self.card_pool:
            if card.player_index == player_index and card.group_index == group_index and card.is_attached():
                attachments.append(card)
        return attachments

    def reveal_card(self, event):
        revealed_card = self.get_hand(event.player_index, event.group_index)[event.card_index]
        if not revealed_card.is_known():
            self.card_pool.remove(revealed_card)
            item_type = gamedata.get_item(event.item_name)
            card_type = gamedata.get_card(event.card_name)
            draw_deck = self.get_draw_deck(event.player_index, event.group_index)
            for card in draw_deck:
                if card.card_type == card_type and card.item_type == item_type:
                    card.draw(event.card_index)
                    break
            else:
                self.players[event.player_index].groups[event.group_index].item_frame.add_item(item_type)
                skipped = False
                for card_type in item_type.cards:
                    if card_type == revealed_card.card_type and not skipped:
                        skipped = True
                        continue
                    for card in draw_deck:
                        if not card.is_known():
                            card.reveal(item_type, card_type)
                            break
                for card in draw_deck:
                    if card.card_type == card_type and card.item_type == item_type:
                        card.draw(event.card_index)
                        break

    def discard_card(self, event):  # TODO: DiscardToOpponent
        self.reveal_card(event)
        # If DiscardToOpponentComponent, wait for genRand to determine where to travel to.
        # components = gamedata.get_card(event.card_name).components
        for card in self.get_hand(event.player_index, event.group_index)[event.card_index:]:
            if card.card_index == event.card_index:
                card.discard()
            elif card.card_index > event.card_index:
                card.card_index -= 1

    def update(self, event):  # TODO
        if event.name == 'Card Draw':
            self.draw_card(event)
        elif event.name == 'Card Reveal':
            self.reveal_card(event)
        elif event.name == 'Card Discard':
            self.discard_card(event)
        elif event.name == 'Card Play':
            self.play_card(event)
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



