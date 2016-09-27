# This file extracts information and a list of battle events from verbose battle logs.

import active_model
import log_parser


# A card related event such as "Draw", "Play", "Show", "Discard"
class CardEvent:
    def __init__(self, event_name, player_turn, original_player_index, original_group_index, player_index, group_index,
                 card_index, card_name, item_name, target_player_indices, target_group_indices):
        self.event = 'Card'
        self.event_name = event_name
        self.player_turn = player_turn
        self.original_player_index = original_player_index
        self.original_group_index = original_group_index
        self.card_index = card_index
        self.card_name = card_name
        self.item_name = item_name
        self.target_player_indices = target_player_indices
        self.target_group_indices = target_group_indices

    def __str__(self):
        return '(%d)[%s] %s - %s' % (self.player_turn, self.event, self.event_name, self.card_name)


# A discard event that does not specify card details.
class DiscardEvent:
    def __init__(self, event_name, player_turn, player_index, group_index, card_index):
        self.event = 'Discard'
        self.event_name = event_name
        self.player_turn = player_turn
        self.player_index = player_index
        self.group_index = group_index
        self.card_index = card_index

    def __str__(self):
        return '(%d)[%s] %s - ' % (self.player_turn, self.event, self.event_name)


# A trigger related event such as "Success", "Failure".
class TriggerEvent:
    def __init__(self, event_name, player_turn, location, player_index, group_index, card_index, x, y, die_roll,
                 required_roll, keep, hard_to_block, easy_to_block):
        self.event = 'Trigger'
        self.event_name = event_name
        self.player_turn = player_turn
        self.location = location
        self.player_index = player_index
        self.group_index = group_index
        self.card_index = card_index
        self.x = x
        self.y = y
        self.die_roll = die_roll
        self.required_roll = required_roll
        self.keep = keep
        self.hard_to_block = hard_to_block
        self.easy_to_block = easy_to_block

    def __str__(self):
        return '(%d)[%s] %s - %s' % (self.player_turn, self.event, self.event_name, ('Hand', 'Attached', 'Terrain')[self.location])


# A target selecting event such as during a step attack.
class TargetEvent:
    def __init__(self, event_name, player_turn, target_player_indices, target_group_indices):
        self.event = 'Target'
        self.event_name = event_name
        self.player_turn = player_turn
        self.target_player_indices = target_player_indices
        self.target_group_indices = target_group_indices

    def __str__(self):
        return '(%d)[%s] %s - ' % (self.player_turn, self.event, self.event_name)


# A tile related event such as selecting a tile to move to.
class TileEvent:
    def __init__(self, event_name, player_turn, x, y, fx, fy):
        self.event = 'Tile'
        self.event_name = event_name
        self.player_turn = player_turn
        self.x = x
        self.y = y
        self.fx = fx
        self.fy = fy

    def __str__(self):
        return '(%d)[%s] %s - (%d, %d)' % (self.player_turn, self.event, self.event_name, self.x, self.y)


# A pass event.
class PassEvent:
    def __init__(self, event_name, player_turn):
        self.event = 'Pass'
        self.event_name = event_name
        self.player_turn = player_turn

    def __str__(self):
        return '(%d)[%s] %s - ' % (self.player_turn, self.event, self.event_name)


log = ''
events = []
battle = active_model.Battle()


# Load the log file into program memory.
def load_log(filename):
    with open(filename) as f:
        global log
        log = f.read()


# Use the log text to construct a sequence of events.
def load_battle():
    # Find the most recent joinbattle and use log_parser.py to parse the battle.
    log_lines = log.splitlines()
    first_line_index = len(log_lines) - 1 - log_lines[::-1].index('Received extension response: joinbattle')
    parsed = log_parser.parse_battle('\n'.join(log_lines[first_line_index:]))

    # Set up the battle by extracting all relevant info from joinbattle.
    player_index = 0
    for obj in parsed[0]['objects']:
        if obj['_class_'] == 'com.cardhunter.battle.Battle':
            battle.scenario_name = obj['scenarioName']
            battle.scenario_display_name = obj['scenarioDisplayName']
            battle.game_type = obj['gameType']
            battle.audio_tag = obj['audioTag']
            battle.room_name = obj['roomName']
        elif obj['_class_'] == 'com.cardhunter.battle.Player':
            player_index = obj['playerIndex']
            player = battle.players[player_index]
            player.name = obj['playerName']
            player.rating = obj['rating']
        elif obj['_class_'] == 'com.cardhunter.battle.Square':
            battle.map.add_square(obj['location.x'], obj['location.y'], obj['imageFlipX'], obj['imageFlipY'],
                                  obj['imageName'], obj['terrain'])
        elif obj['_class_'] == 'com.cardhunter.battle.Doodad':
            battle.map.add_doodad(obj['displayPosition.x'], obj['displayPosition.y'], obj['imageFlipX'],
                                  obj['imageFlipY'], obj['imageName'], obj['marker'])
        elif obj['_class_'] == 'com.cardhunter.battle.ActorGroup':
            for actor in battle.players[player_index].team:
                if not actor.is_described():
                    actor.name = obj['name']
                    actor.set_archetype(obj['race'] + ' ' + obj['characterClass'])
                    break
        elif obj['_class_'] == 'com.cardhunter.battle.ActorInstance':
            for actor in battle.players[player_index].team:
                if not actor.is_described():
                    actor.figure = obj['depiction']
                    actor.audio_key = obj['audioKey']
                    actor.x = obj['location.x']
                    actor.y = obj['location.y']
                    actor.fx = obj['facing.x']
                    actor.fy = obj['facing.y']
                    break

    # Figure out who the enemy is and construct a sequence of 'events'.
    must_discard = [-1, -1]
    player_turn = -1
    global events
    for ex in parsed[1:]:
        if ex.name == 'battleTimer':
            player_index = ex['playerIndex']
            if ex['start']:
                player_turn = player_index
            else:
                player_turn = -1
        if ex.name != 'battle':
            continue
        if ex['type'] in ('deckPeeks', 'handPeeks', 'action'):
            # Map the extension response type to the relevant event name.
            event_name = {'deckPeeks': 'Draw', 'handPeeks': 'Show', 'action': 'Play'}[ex['type']]

            # Set the value of peek to view the card info.
            # If this is a deckPeeks, use it to figure out who the user is and who the enemy is.
            peek = 'HP'
            if ex['type'] == 'deckPeeks':
                peek = 'DP'
                if battle.enemy is None:
                    battle.set_enemy(1 - ex['SENDID'][0])

            # If this is a "Play" event, determine the targets.
            target_player_indices = []
            target_group_indices = []
            if 'TARG' in ex:
                target_group_indices = ex['TARG']
                target_player_indices = ex['TARP']

            # For every card in the peeks array, extract its info and append an event for it.
            for info in ex[peek]['peeks']:
                original_player_index = info['cownerp']
                original_group_index = info['cownerg']
                card_index = info['card']
                card_name = info['type']
                item_name = info['origin']
                player_index = info['owner']
                group_index = info['group']
                events.append(CardEvent(event_name, player_turn, original_player_index, original_group_index,
                                        player_index, group_index, card_index, card_name, item_name,
                                        target_player_indices, target_group_indices))
        elif ex['type'] == 'selectCard':
            event_name = 'Discard'
            if 'HP' in ex:
                info = ex['HP']['peeks'][0]
                original_player_index = info['cownerp']
                original_group_index = info['cownerg']
                card_index = info['card']
                card_name = info['type']
                item_name = info['origin']
                player_index = info['owner']
                group_index = info['group']
                events.append(CardEvent(event_name, player_turn, original_player_index, original_group_index,
                                        player_index, group_index, card_index, card_name, item_name, [], []))
            else:
                selected_player_index = must_discard[0]
                selected_group_index = must_discard[1]
                selected_card_index = ex['sel']
                events.append(DiscardEvent(event_name, player_turn, selected_player_index, selected_group_index,
                                           selected_card_index))
        elif ex['type'] == 'selectCards':
            if 'SELP' in ex:
                event_name = 'Discard'
                selected_player_indices = ex['SELP']
                selected_group_indices = ex['SELG']
                selected_card_indices = ex['SELCC']
                for i in range(len(selected_player_indices)):
                    events.append(DiscardEvent(event_name, player_turn, selected_player_indices[i],
                                               selected_group_indices[i], selected_card_indices[i]))
        elif ex['type'] == 'mustDiscard':
            must_discard[0] = ex['PUI']
            must_discard[1] = ex['ACTG']
        elif ex['type'] in ('triggerFail', 'triggerSucceed') and 'TCLOC' in ex:
            event_name = {'triggerSucceed': 'Success', 'triggerFail': 'Failure'}[ex['type']]
            location = ex['TCLOC']
            player_index = group_index = card_index = x = y = None
            if location != 2:
                player_index = ex['PUI']
                group_index = ex['ACTG']
            else:
                x = ex['TARX']
                y = ex['TARY']
            if location == 0:
                card_index = ex['ACTC']
            die_roll = ex['TROLL']
            required_roll = ex['TTHRESH']
            keep = ex['DTHRESH'] != 8
            hard_to_block = ex['TPEN']
            easy_to_block = ex['TBON']
            events.append(TriggerEvent(event_name, player_turn, location, player_index, group_index, card_index, x, y,
                                       die_roll, required_roll, keep, hard_to_block, easy_to_block))
        elif ex['type'] == 'target':
            event_name = 'Select'
            target_player_indices = ex['TARP']
            target_group_indices = ex['TARG']
            events.append(TargetEvent(event_name, player_turn, target_player_indices, target_group_indices))
        elif ex['type'] == 'selectSquare':
            event_name = 'Select'
            x = ex['TARX']
            y = ex['TARY']
            fx = ex['TARFX']
            fy = ex['TARFY']
            events.append(TileEvent(event_name, player_turn, x, y, fx, fy))
        elif ex['type'] == 'pass':
            event_name = 'Pass'
            events.append(PassEvent(event_name, player_turn))
