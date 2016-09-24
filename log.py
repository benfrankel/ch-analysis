# This file extracts information and a list of battle events from verbose battle logs.

import active_model
import log_parser


log = ''
events = []
battle = active_model.Battle()


def load_log(filename):
    with open(filename) as f:
        global log
        log = f.read()


def update_battle():
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
    for ex in parsed[1:]:
        if ex.name != 'battle':
            continue
        if ex['type'] == 'deckPeeks':
            # Event is DrawCard.
            if battle.enemy is None:
                battle.set_enemy(1 - ex['SENDID'][0])
            info = ex['DP']['peeks'][0]
            card_index = info['card']
            card_name = info['type']
            item_name = info['origin']
            player_index = info['owner']
            actor_index = info['group']
            original_player_index = info['cownerp']
            original_actor_index = info['cownerg']
        elif ex['type'] == 'handPeeks':
            # Event is RevealCard.
            info = ex['HP']['peeks'][0]
            card_index = info['card']
            card_name = info['type']
            item_name = info['origin']
            player_index = info['owner']
            actor_index = info['group']
            original_player_index = info['cownerp']
            original_actor_index = info['cownerg']
        elif ex['type'] == 'action':
            pass
        elif ex['type'] == 'selectCard':
            pass
        elif ex['type'] == 'selectCards':
            pass
        elif ex['type'] == 'triggerSuccess':
            pass
        elif ex['type'] == 'triggerFail':
            pass
        elif ex['type'] == 'target':
            pass
        elif ex['type'] == 'pass':
            pass

    # Some other class will be able to deal with the list of events. We can just return the list.

