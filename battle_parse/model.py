import enum

import gamedata
from .event import *


# Card instance during a battle (type may be hidden)
class Card:
    def __init__(self):
        # Info
        self.name = None
        self.type = None
        self.item_name = None

        # State
        self.original_player_index = None
        self.original_group_index = None
        self.visible = None

    def is_described(self):
        return (\
            self.original_player_index is not None and\
            self.original_group_index is not None and\
            self.visible is not None and\
            not self.visible or (\
                self.name is not None and\
                self.card_type is not None and\
                self.item_type is not None and\
            True) and\
        True)

    def reveal(self, name, item_name):
        self.name = name
        self.type = gamedata.get_card(name)
        self.item_name = item_name
        
        try:
            self.item_type = gamedata.get_item(item_name)
        except KeyError:
            self.item_type = None

    def is_hidden(self):
        return self.card_type is None

    def __str__(self):
        return self.name or '?'

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# Item instance during a battle (type may be hidden)
class Item:
    def __init__(self, num_cards):
        # Info
        self.name = None
        self.item_type = None

        # Children
        self.cards = [Card() for _ in range(3)]

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
        return '?' if self.name is None else self.name

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# Item slot instance (e.g. Weapon, Staff, Divine Skill) that can contain an Item during a battle
class ItemSlot:
    def __init__(self, name):
        # Info
        self.name = name
        self.num_cards = 6 if name in ('Weapon', 'Divine Weapon', 'Staff') else 3

        # Children
        self.item = Item(self.num_cards)

    def set_item_type(self, item_type):
        if item_type.slot_type != self.name:
            raise ValueError('Cannot place "{}" ({}) in {} slot'.format(item_type.name, item_type.slot_type, self.name))

        self.item.reveal(item_type)

    def remove_item(self):
        self.item = Item(self.num_cards)

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
    def __init__(self):
        # Info
        self.name = None
        self.archetype = None

        # Children
        self.slot_types = None
        self.slots = None

    def is_described(self):
        return (
            self.name is not None and
            self.archetype is not None and
            self.slot_types is not None and
            self.slots is not None and
        True)

    def set_archetype(self, archetype):
        self.archetype = archetype
        self.name = archetype.name
        self.slot_types = archetype.slot_types
        self.slots = [ItemSlot(slot_type) for slot_type in self.slot_types]

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
        return ', '.join(str(slot) for slot in self.slots) if self.slots is not None else '?'

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)

class Actor:
    def __init__(self):
        # Info
        self.name = None
        self.figure = None
        self.figure_size = None
        self.audio_key = None
        self.star_value = None

        # State
        self.max_hp = None
        self.hp = None
        self.ap = None
        self.attachments = []
        self.attachment_durations = []

        # Placement
        self.x = None
        self.y = None
        self.fx = None
        self.fy = None

    @property
    def alive(self):
        return self.hp > 0

    def is_described(self):
        return (
            self.name is not None and
            self.figure is not None and
            self.figure_size is not None and
            self.audio_key is not None and
            self.star_value is not None and
            self.max_hp is not None and
            self.hp is not None and
            self.ap is not None and
            self.x is not None and
            self.y is not None and
            self.fx is not None and
            self.fy is not None and
        True)

# Actor group during a battle (name, figure, archetype, item frame)
class Group:
    def __init__(self):
        # Info
        self.name = None
        self.display_name = None
        self.archetype = None
        self.base_ap = None
        self.draws_per_actor = None
        self.draw_limit = None

        # Children
        self.item_frame = ItemFrame()
        self.actors = []
        self.draw_deck = None
        self.discard_deck = None
        self.hand = None

    @property
    def living_actors(self):
        return [a for a in self.actors if a.alive]

    @property
    def num_draws(self):
        base_draws = int(len(self.alive_actors) * self.draws_per_actor)
        return max(base_draws, 1) + (self.player.battle.current_round == 0)

    def add_actor(self, actor):
        actor.group = self
        actor.index = len(self.actors)
        self.actors.append(actor)
        return actor

    def register_actor(self, obj_at, idx):
        if idx in obj_at:
            self.add_actor(obj_at[idx])
        else:
            obj_at[idx] = self.add_actor(Actor())

    def is_described(self):
        return (
            self.name is not None and
            self.display_name is not None and
            self.archetype is not None and
            self.base_ap is not None and
            self.draws_per_actor is not None and
            self.draw_limit is not None and
            self.index is not None and
            self.player is not None and
            self.item_frame.is_described() and
            self.draw_deck is not None and
            self.discard_deck is not None and
            self.hand is not None and
            all(a.is_described() for a in self.actors) and
        True)

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
        print('Playing card ...')
        self.discard_card(event)
        pass  # TODO

    def __str__(self):
        return '{} ({} {})\nEquipment: {}'.format(
            self.name or '?',
            self.archetype.race if self.archetype is not None else '?',
            self.archetype.role if self.archetype is not None else '?',
            self.item_frame,
        )

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.name)


# Player during a battle
class Player:
    def __init__(self):
        # Info
        self.name = None
        self.player_id = None
        self.user_id = None
        self.is_npc = None
        self.rating = None
        self.draw_limit = None
        self.cards_drawn = None
        self.stars_needed = None

        # State
        self.stars = None
        self.drawing_group = 0

        # Children
        self.groups = []

    def add_group(self, group):
        group.player = self
        group.index = len(self.groups)
        self.groups.append(group)
        return group

    def register_group(self, obj_at, idx):
        if idx in obj_at:
            self.add_group(obj_at[idx])
        else:
            obj_at[idx] = self.add_group(Group())

    def is_described(self):
        return (
            self.name is not None and
            self.player_id is not None and
            self.user_id is not None and
            self.rating is not None and
            self.is_npc is not None and
            self.stars is not None and
            self.stars_needed is not None and
            self.cards_drawn is not None and
            self.draw_limit is not None and
            all(g.is_described() for g in self.groups) and
        True)

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


# Board square during a battle
class Square:
    def __init__(self,
        x=None,
        y=None,
        flip_x=None,
        flip_y=None,
        image_name=None,
        terrain=None
    ):
        # Info
        self.image_name = image_name
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.terrain = terrain

        # State
        self.attachment = None
        self.duration = None

        # Placement
        self.x = x
        self.y = y


# Board doodad during a battle (static; doodads stay the same throughout the battle)
class Doodad:
    def __init__(self,
        x=None,
        y=None,
        flip_x=None,
        flip_y=None,
        image_name=None,
        marker=None,
    ):
        # Info
        self.image_name = image_name
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.marker = marker  # TODO: What is this?

        # Placement
        self.x = x
        self.y = y


# Board during a battle (bunch of tiles and doodads)
class Board:
    square_char =  {
        'Open': '.',
        'Difficult': '-',
        'Impassable': 'o',
        'Blocked': '#',
        'Victory': '@',
    }
            
    def __init__(self):
        # Info
        self.w = None
        self.h = None

        # Children
        self.squares = []
        self.square_at = {}
        self.doodads = []

    def is_described(self):
        return (
            self.w is not None and
            self.h is not None and
        True)

    def add_square(self, square):
        square.board = self
        self.squares.append(square)
        return square

    def register_square(self, obj_at, idx):
        if idx in obj_at:
            self.add_square(obj_at[idx])
        else:
            obj_at[idx] = self.add_square(Square())

    def add_doodad(self, doodad):
        doodad.board = self
        self.doodads.append(doodad)
        return doodad

    def register_doodad(self, obj_at, idx):
        if idx in obj_at:
            self.add_doodad(obj_at[idx])
        else:
            obj_at[idx] = self.add_doodad(Doodad())

    def get_square(self, x, y):
        return self.square_at[x, y]

    def build(self):
        for square in self.squares:
            self.square_at[square.x, square.y] = square

    def _square_to_char(self, x, y):
        if (x, y) in self.square_at:
            return Board.square_char[self.square_at[x, y].terrain]
        return ' '

    def __str__(self):
        return '\n'.join(''.join(self._square_to_char(x, y) for y in range(self.h)) for x in range(self.w))


# Battle (board, players, actors, cards, items, etc.)
class Battle:
    def __init__(self):
        # Info
        self.scenario_name = None
        self.display_name = None
        self.room_name = None
        self.room_id = None
        self.time_limit = None
        self.use_draw_limit = None
        self.game_type = None
        self.audio_tag = None
        self.respawn_period = None
        self.win_on_all_dead = None

        # State
        self.current_turn = None
        self.current_round = None
        self.game_over = None

        # Children
        self.board = Board()
        self.players = []
        self.user = None
        self.enemy = None

    def add_player(self, player):
        player.battle = self
        player.index = len(self.players)
        self.players.append(player)
        return player

    def register_player(self, obj_at, idx):
        if idx in obj_at:
            self.add_player(obj_at[idx])
        else:
            obj_at[idx] = self.add_player(Player())

    def set_user(self, user_index):
        self.user = self.players[user_index]
        self.enemy = self.players[1 - user_index]

    def is_described(self):
        return (
            self.scenario_name is not None and
            self.display_name is not None and
            self.room_name is not None and
            self.room_id is not None and
            self.time_limit is not None and
            self.use_draw_limit is not None and
            self.game_type is not None and
            self.audio_tag is not None and
            self.respawn_period is not None and
            self.win_on_all_dead is not None and
            self.current_turn is not None and
            self.current_round is not None and
            self.game_over is not None and
            self.board.is_described() and
            all(p.is_described() for p in self.players) and
        True)

    def build(self):
        if not self.is_described():
            print(self.players[0].groups[0].__dict__)
            raise ValueError('Battle is not fully described')
        
        self.board.build()

    def update(self, event):  # TODO
        try:
            print('    |', event)
            print('    | Hand before:', self.players[event.player_index].groups[event.group_index].hand)
        except Exception:
            pass

        # TODO: Fix traits (Must Play Trait -> No More Traits)
        # TODO: In the interim, REPLACE cards played by enemy
        # TODO: What about cards drawn by user? How do you know what should be replaced by the new card?

        if isinstance(event, CardDraw):
            self.players[event.player_index].reveal_card(event, from_deck=True)
            self.players[event.player_index].draw_card(event)
        elif isinstance(event, HiddenDraw):
            self.enemy.hidden_draw()
        elif isinstance(event, CardReveal):
            self.players[event.player_index].reveal_card(event)
        elif isinstance(event, CardDiscard):
            self.players[event.player_index].reveal_card(event)
            self.players[event.player_index].discard_card(event)
        elif isinstance(event, CardPlay):
            self.players[event.player_index].reveal_card(event)
            self.players[event.player_index].play_card(event)
        elif isinstance(event, SelectTarget):
            pass
        elif isinstance(event, SelectSquare):
            pass
        elif isinstance(event, TriggerHand):
            pass
        elif isinstance(event, TriggerAttachment):
            pass
        elif isinstance(event, TriggerTerrain):
            pass
        elif isinstance(event, Pass):
            pass

        try:
            print('    | Hand after:', self.players[event.player_index].groups[event.group_index].hand)
        except Exception:
            pass
