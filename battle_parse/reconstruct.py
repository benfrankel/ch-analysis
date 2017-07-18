# This file extracts information and a list of battle events from verbose battle logs

from tkinter import Tk

from util import log_parse
from . import model


# Basic superclass for all events
class Event:
    def __init__(self, name, player_turn):
        self.name = name
        self.player_turn = player_turn

    def __str__(self):
        return '({:2}) {}'.format(self.player_turn, self.name)


# Superclass for all card-related events
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
        return super().__str__() + ' [{} : {}]'.format(self.card_name, self.item_name)


# A card play event
class PlayEvent(CardEvent):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Play', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# A card draw event
class DrawEvent(CardEvent):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Draw', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# An unrevealed card draw event
class HiddenDrawEvent(Event):
    def __init__(self, player_turn):
        super().__init__('Hidden Draw', player_turn)

    def __str__(self):
        return super().__str__()


# A card reveal event
class RevealEvent(CardEvent):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Reveal', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# A card discard event
class DiscardEvent(CardEvent):
    def __init__(self, player_turn, original_player_index, original_group_index, player_index, group_index, card_index,
                 item_name, card_name):
        super().__init__('Discard', player_turn, original_player_index, original_group_index, player_index, group_index,
                         card_index, item_name, card_name)

    def __str__(self):
        return super().__str__()


# Superclass for trigger related events such as "Success", "Failure"
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
class HandEvent(TriggerEvent):
    def __init__(self, player_turn, die_roll, required_roll, hard_to_block, easy_to_block, player_index,
                 group_index, card_index):
        super().__init__('Hand', player_turn, die_roll, required_roll, hard_to_block, easy_to_block)
        self.player_index = player_index
        self.group_index = group_index
        self.card_index = card_index

    def __str__(self):
        return super().__str__()


# Trigger event where the card is an attachment
class AttachmentEvent(TriggerEvent):
    def __init__(self, player_turn, die_roll, required_roll, hard_to_block, easy_to_block, player_index, group_index):
        super().__init__('Attachment', player_turn, die_roll, required_roll, hard_to_block, easy_to_block)
        self.player_index = player_index
        self.group_index = group_index


# Trigger event where the card is a terrain attachment
class TerrainEvent(TriggerEvent):
    def __init__(self, player_turn, die_roll, required_roll, hard_to_block, easy_to_block, x, y):
        super().__init__('Terrain', player_turn, die_roll, required_roll, hard_to_block, easy_to_block)
        self.x = x
        self.y = y

    def __str__(self):
        return super().__str__()


# A target selection event such as for a step attack
class TargetEvent(Event):
    def __init__(self, player_turn, target_player_indices, target_group_indices):
        super().__init__('Target', player_turn)
        self.target_player_indices = target_player_indices
        self.target_group_indices = target_group_indices

    def __str__(self):
        return super().__str__()


# A square selection event such as for movement
class SquareEvent(Event):
    def __init__(self, player_turn, x, y, fx, fy):
        super().__init__('Square', player_turn)
        self.x = x
        self.y = y
        self.fx = fx
        self.fy = fy

    def __str__(self):
        return super().__str__() + ' [{}, {}]'.format(self.x, self.y)


# A random number generation event
class RandomEvent(Event):
    def __init__(self, player_turn, rands):
        super().__init__('Random', player_turn)
        self.rands = rands

    def __str__(self):
        return super().__str__()


# A pass event
class PassEvent(Event):
    def __init__(self, player_turn):
        super().__init__('Pass', player_turn)

    def __str__(self):
        return super().__str__()


# Use the log text to construct a sequence of events that can be fed into a Battle
def load_battle(filename=''):
    events = []
    scenario = model.Scenario()

    def update_scenario():
        scenario.update(events[-1])

    # Load log contents into memory
    if filename == '':
        root = Tk()
        root.withdraw()
        try:
            log = root.clipboard_get()
        except:
            return events, scenario
        if 'Received extension response: joinbattle' not in log:
            return events, scenario
    else:
        with open(filename) as f:
            log = f.read()

    # Find the most recent joinbattle and use log_parse.py to parse the battle_parse
    log_lines = log.splitlines()
    first_line_index = len(log_lines) - 1 - log_lines[::-1].index('Received extension response: joinbattle')
    extension_responses, messages = log_parse.parse_battle('\n'.join(log_lines[first_line_index:]))

    # Set up the battle_parse by extracting all relevant info from joinbattle
    for obj in extension_responses[0]['objects']:
        if obj['_class_'] == 'com.cardhunter.battle_parse.Battle':
            scenario.name = obj['scenarioName']
            scenario.display_name = obj['scenarioDisplayName']
            scenario.game_type = obj['gameType']
            scenario.audio_tag = obj['audioTag']
            scenario.room_name = obj['roomName']
        elif obj['_class_'] == 'com.cardhunter.battle_parse.Player':
            player_index = obj['playerIndex']
            player = scenario.players[player_index]
            player.name = obj['playerName']
            player.rating = obj['rating']
        elif obj['_class_'] == 'com.cardhunter.battle_parse.Square':
            scenario.map.add_square(obj['location.x'], obj['location.y'], obj['imageFlipX'], obj['imageFlipY'],
                                    obj['imageName'], obj['terrain'])
        elif obj['_class_'] == 'com.cardhunter.battle_parse.Doodad':
            scenario.map.add_doodad(obj['displayPosition.x'], obj['displayPosition.y'], obj['imageFlipX'],
                                    obj['imageFlipY'], obj['imageName'], obj['marker'])
        elif obj['_class_'] == 'com.cardhunter.battle_parse.ActorGroup':
            for group in scenario.players[0].groups + scenario.players[1].groups:
                if not group.is_described():
                    group.name = obj['name']
                    group.set_archetype(' '.join([obj['race'], obj['characterClass']]))
                    break
        elif obj['_class_'] == 'com.cardhunter.battle_parse.ActorInstance':
            for group in scenario.players[0].groups + scenario.players[1].groups:
                if not group.is_described():
                    group.figure = obj['depiction']
                    group.audio_key = obj['audioKey']
                    group.x = obj['location.x']
                    group.y = obj['location.y']
                    group.fx = obj['facing.x']
                    group.fy = obj['facing.y']
                    break

    if not scenario.is_described():
        pass  # Scenario not completely started

    # Figure out who the enemy is and construct a sequence of events
    must_discard = [-1, -1]
    player_turn = -1
    for ex, prev in zip(extension_responses[1:], extension_responses):
        if ex.name == 'battleTimer':
            player_index = ex['playerIndex']
            if ex['start']:
                player_turn = player_index
            else:
                player_turn = -1

        if ex.name != 'battle_parse':
            continue

        if ex['type'] == 'deckPeeksSent' and ('type' not in prev or prev['type'] != 'deckPeeks'):
            events.append(HiddenDrawEvent(player_turn))
            update_scenario()

        if ex['type'] == 'deckPeeks':
            # If the user is still unknown, use this deckPeeks to determine who it is
            if scenario.user is None:
                scenario.set_user(ex['SENDID'][0])

            # For every card in the peeks array, extract its info and append an event for it
            for info in ex['DP']['peeks']:
                original_player_index = info['cownerp']
                original_group_index = info['cownerg']
                card_index = info['card']
                item_name = info['origin']
                card_name = info['type']
                player_index = info['owner']
                group_index = info['group']
                events.append(DrawEvent(player_turn, original_player_index, original_group_index, player_index,
                                        group_index, card_index, item_name, card_name))
                update_scenario()
        elif ex['type'] == 'handPeeks':
            # For every card in the peeks array, extract its info and append an event for it
            for info in ex['HP']['peeks']:
                original_player_index = info['cownerp']
                original_group_index = info['cownerg']
                card_index = info['card']
                item_name = info['origin']
                card_name = info['type']
                player_index = info['owner']
                group_index = info['group']
                events.append(RevealEvent(player_turn, original_player_index, original_group_index, player_index,
                                          group_index, card_index, item_name, card_name))
                update_scenario()
        elif ex['type'] == 'action':
            # For every card in the peeks array, extract its info and append an event for it
            for info in ex['HP']['peeks']:
                original_player_index = info['cownerp']
                original_group_index = info['cownerg']
                card_index = info['card']
                item_name = info['origin']
                card_name = info['type']
                player_index = info['owner']
                group_index = info['group']
                events.append(PlayEvent(player_turn, original_player_index, original_group_index, player_index,
                                        group_index, card_index, item_name, card_name))
                if 'TARP' in ex:
                    target_player_indices = ex['TARP']
                    target_group_indices = ex['TARG']
                    events.append(TargetEvent(player_turn, target_player_indices, target_group_indices))
                    update_scenario()
        elif ex['type'] == 'selectCard':
            if 'HP' in ex:
                for info in ex['HP']['peeks']:
                    original_player_index = info['cownerp']
                    original_group_index = info['cownerg']
                    card_index = info['card']
                    item_name = info['origin']
                    card_name = info['type']
                    player_index = info['owner']
                    group_index = info['group']
                    events.append(DiscardEvent(player_turn, original_player_index, original_group_index, player_index,
                                               group_index, card_index, item_name, card_name))
                    update_scenario()
            else:
                player_index = must_discard[0]
                group_index = must_discard[1]
                card_index = ex['sel']
                try:
                    card = scenario.players[player_index].groups[group_index].hand[card_index]
                    original_player_index = card.original_player_index
                    original_group_index = card.original_group_index
                    item_name = card.item_name
                    card_name = card.card_name
                    events.append(DiscardEvent(player_turn, original_player_index, original_group_index, player_index,
                                               group_index, card_index, item_name, card_name))
                except:
                    pass
        # elif ex['type'] == 'selectCards':
        #     if 'SELP' in ex:
        #         selected_player_indices = ex['SELP']
        #         selected_group_indices = ex['SELG']
        #         selected_card_indices = ex['SELCC']
        #         for i in range(len(selected_player_indices)):
        #             events.append(SelectEvent(player_turn, selected_player_indices[i], selected_group_indices[i],
        #                                       selected_card_indices[i]))
        elif ex['type'] == 'mustDiscard':
            must_discard[0] = ex['PUI']
            must_discard[1] = ex['ACTG']
        elif ex['type'] in ('triggerFail', 'triggerSucceed') and 'TCLOC' in ex:
            die_roll = ex['TROLL']
            required_roll = ex['TTHRESH']
            hard_to_block = ex['TPEN']
            easy_to_block = ex['TBON']
            location = ex['TCLOC']
            if location == 0:
                player_index = ex['PUI']
                group_index = ex['ACTG']
                card_index = ex['ACTC']
                events.append(HandEvent(player_turn, die_roll, required_roll, hard_to_block, easy_to_block, player_index,
                                        group_index, card_index))
                update_scenario()
            elif location == 1:
                player_index = ex['PUI']
                group_index = ex['ACTG']
                events.append(AttachmentEvent(player_turn, die_roll, required_roll, hard_to_block, easy_to_block,
                                              player_index, group_index))
                update_scenario()
            elif location == 2:
                x = ex['TARX']
                y = ex['TARY']
                events.append(TerrainEvent(player_turn, die_roll, required_roll, hard_to_block, easy_to_block, x, y))
                update_scenario()
        elif ex['type'] == 'target':
            target_player_indices = ex['TARP']
            target_group_indices = ex['TARG']
            events.append(TargetEvent(player_turn, target_player_indices, target_group_indices))
            update_scenario()
        elif ex['type'] == 'selectSquare':
            x = ex['TARX']
            y = ex['TARY']
            fx = ex['TARFX']
            fy = ex['TARFY']
            events.append(SquareEvent(player_turn, x, y, fx, fy))
            update_scenario()
        elif ex['type'] == 'pass':
            events.append(PassEvent(player_turn))
            update_scenario()

    return events, scenario
