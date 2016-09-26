# This file extracts information and a list of battle events from verbose battle logs.

import active_model
import log_parser


# A card related event such as "Draw", "Play", "Show", "Discard".
class CardEvent:
    def __init__(self, event_name, original_player_index, original_actor_index, player_index, actor_index, card_index,
                 card_name, item_name, target_players, target_actors):
        self.event_name = event_name
        self.original_player_index = original_player_index
        self.original_actor_index = original_actor_index
        self.player_index = player_index
        self.actor_index = actor_index
        self.card_index = card_index
        self.card_name = card_name
        self.item_name = item_name
        self.targets = [battle.players[player].team[actor] for player, actor in zip(target_players, target_actors)]


# A trigger related event such as "Success", "Failure".
class TriggerEvent:
    def __init__(self, event_name):
        self.event_name = event_name


log = ''
events = []
battle = active_model.Battle()


# Load the log file into program memory.
def load_log(filename):
    with open(filename) as f:
        global log
        log = f.read()


# Use the log text to construct a sequence of events.
def update_battle():
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

    # Figure out who the enemy is and create a list of "events".
    events = []
    for ex in parsed[1:]:
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
            target_players = []
            target_actors = []
            if 'TARG' in ex:
                target_actors = ex['TARG']
                target_players = ex['TARP']

            # For every card in the peeks array, extract its info and append an event for it.
            for info in ex[peek]['peeks']:
                original_player_index = info['cownerp']
                original_actor_index = info['cownerg']
                card_index = info['card']
                card_name = info['type']
                item_name = info['origin']
                player_index = info['group']
                actor_index = info['owner']
                events.append(CardEvent(event_name, original_player_index, original_actor_index, player_index,
                                        actor_index, card_index, card_name, item_name, target_players, target_actors))
        elif ex['type'] == 'selectCard':
            pass
        elif ex['type'] == 'selectCards':
            pass
        elif ex['type'] == 'triggerSucceed':
            # Not yet implemented.
            events.append(TriggerEvent())
        elif ex['type'] == 'triggerFail':
            pass
        elif ex['type'] == 'target':
            pass
        elif ex['type'] == 'pass':
            pass
        elif ex['type'] == 'selectSquare':
            pass

    # Some other class will be able to deal with the list of events. We can just return the list.

