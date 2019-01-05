import enum

import gamedata
from .event import *


# Card instance during a battle (type may be hidden)
class Card:
    def __init__(self):
        # Info
        self.type = None
        self.origin = None
        self.item_type = None
        self.created = None
        self.original_group = None

        # State
        self.visible = None

    def is_described(self):
        return (
            self.visible is not None and
            not self.visible or (
                self.type is not None and
                self.origin is not None and
                self.created is not None and
                self.created or (
                    self.original_group is not None and
                True) and
            True) and
        True)

    def reveal(self, card_type, origin):
        if not self.is_hidden() and (self.type != card_type or self.origin != origin):
            raise ValueError('Cannot reveal "{}" from "{}" as "{}" from "{}"'.format(
                self.type, self.origin, card_type, origin))
        
        self.type = card_type
        self.origin = origin
        
        try:
            self.item_type = gamedata.get_item(origin)
        except KeyError:
            self.item_type = None

    def is_hidden(self):
        return self.type is None

    def __str__(self):
        return '?' if self.type is None else self.type.name

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.type)


# Item instance during a battle (type may be hidden)
class Item:
    def __init__(self):
        # Info
        self.type = None

        # State
        self.marked = None

    def reveal(self, type_):
        self.type = type_
        self.marked = [False] * len(type_.cards)

    def try_mark(self, card):
        for i, card_type in enumerate(self.type.cards):
            if self.marked[i] is card:
                return True
            if self.marked[i] is not None and card_type == card.type:
                self.marked[i] = True
                return True
        return False

    def reshuffle(self):
        for card in self.cards:
            card.reshuffle()

    def is_hidden(self):
        return self.type is None

    def __contains__(self, card_type):
        for card in self.cards:
            if card.type == card_type:
                return True
        return False

    def __eq__(self, other):
        return self.type == other.type

    def __str__(self):
        return '?' if self.type is None else self.type.name

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.type)


# Item slot instance (e.g. Weapon, Staff, Divine Skill) that can contain an Item during a battle
class ItemSlot:
    def __init__(self, name):
        # Info
        self.name = name

        # Children
        self.num_cards = 6 if name in ('Weapon', 'Divine Weapon', 'Staff') else 3
        self.item = Item()

    def set_item_type(self, item_type):
        if item_type.slot_type != self.name:
            raise ValueError('Cannot place "{}" ({}) in {} slot'.format(item_type.name, item_type.slot_type, self.name))

        self.item.reveal(item_type)

    def remove_item(self):
        self.item = Item(self.num_cards)

    def is_empty(self):
        return self.item.is_hidden()

    def __contains__(self, item_type):
        return self.item.type == item_type

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

    def mark(self, card):
        for slot in self.slots:
            if slot.item.type == card.item_type and slot.item.try_mark(card):
                return

        item = self.add_item(card.item_type)
        if not item.try_mark(card):
            raise ValueError('Cannot mark "{}" from item "{}"'.format(card.type, card.item_type))

    def add_item(self, item_type):
        for slot in self.slots:
            if slot.name == item_type.slot_type and slot.is_empty():
                slot.item.reveal(item_type)
                return slot.item
    
        raise ValueError('Cannot add "{}" ({}) to {} Frame without such a slot open'.format(item_type.name, item_type.slot_type, self.name))

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

    def build(self):
        pass

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
            all(c.is_described() for c in self.draw_deck) and
            all(c.is_described() for c in self.discard_deck) and
            all(c.is_described() for c in self.hand) and
            all(a.is_described() for a in self.actors) and
        True)

    def build(self):
        for actor in self.actors:
            actor.build()

    def set_archetype(self, archetype):
        self.archetype = archetype
        self.item_frame.set_archetype(archetype)

    def reshuffle(self):
        self.draw_deck.extend(self.discard_deck)
        self.discard_deck.clear()

    def discard(self, card_index):
        card = self.hand.pop(card_index)
        
        if card.is_hidden():
            raise ValueError('Must reveal card before discarding')
        
        self.discard_deck.append(card)

    def draw(self):
        card = self.draw_deck.pop()
        self.hand.insert(0, card)

    def __str__(self):
        return '{} ({} {})\nEquipment: {}'.format(
            '?' if self.name is None else self.name,
            '?' if self.archetype is None else self.archetype.race,
            '?' if self.archetype is None else self.archetype.role,
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

    def build(self):
        for group in self.groups:
            group.build()


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
        row = lambda y: ''.join(self._square_to_char(x, y) for x in range(self.w))
        return '\n'.join(map(row, range(self.h)))


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
        self.cards = []
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
            raise ValueError('Battle is not fully described')
        
        self.board.build()
        
        for player in self.players:
            player.build()

        for card in self.cards:
            if card.item_type is None:
                continue

            card.original_group.item_frame.mark(card)

        for player in self.players:
            for group in player.groups:
                print(group)
                print()

    def reveal_card(self, event):
        player = self.players[event.player_index]
        group = player.groups[event.group_index]
        card = group.hand[event.card_index]
        card.reveal(event.card_type, event.origin)

        if event.original_player_index != -1:
            if card.item_type is None:
                raise KeyError('Unknown item "{}"'.format(card.origin))
            
            original_player = self.players[event.original_player_index]
            original_group = original_player.groups[event.original_group_index]
            original_group.item_frame.mark(card)

    def update(self, event):  # TODO
        try:
            print(event)
            print('    : Hand before =', self.players[event.player_index].groups[event.group_index].hand)
        except:
            pass

        if isinstance(event, ExCardReveal):
            self.reveal_card(event)
                
        elif isinstance(event, ExCardDraw):
            pass
        
        elif isinstance(event, ExCardDiscard):
            pass
        
        elif isinstance(event, ExCardPlay):
            player = self.players[event.player_index]
            group = player.groups[event.group_index]
            card = group.hand[event.card_index]

            # TODO: What if Unstoppable Chop is blocked and returned to hand?
            # TODO: DiscardToOpponentComponent => Wait for genRand to determine where to travel to
            group.discard(event.card_index)

            for param, value in card.type.components.items():
                if param == 'DrawOnResolveComponent':
                    group.draw()
                else:
                    print('Ignored component: {} = {}'.format(param, value))
        
        elif isinstance(event, ExMustTrait):
            pass
        
        elif isinstance(event, ExNoTraits):
            pass
        
        elif isinstance(event, ExMustDiscard):
            pass
        
        elif isinstance(event, ExNoDiscards):
            pass
        
        elif isinstance(event, ExHandPeek):
            pass
        
        elif isinstance(event, ExDeckPeek):
            pass
        
        elif isinstance(event, ExTriggerInHand):
            pass
        
        elif isinstance(event, ExTriggerTrait):
            pass
        
        elif isinstance(event, ExTriggerTerrain):
            pass
        
        elif isinstance(event, ExSelectTarget):
            pass
        
        elif isinstance(event, ExSelectSquare):
            pass
        
        elif isinstance(event, ExRNG):
            pass
        
        elif isinstance(event, ExRespawn):
            pass
        
        elif isinstance(event, ExStartTimer):
            pass
        
        elif isinstance(event, ExPauseTimer):
            pass
        
        elif isinstance(event, ExPass):
            pass
        
        elif isinstance(event, ExResign):
            pass

        try:
            print('    : Hand after  =', self.players[event.player_index].groups[event.group_index].hand)
        except:
            pass
