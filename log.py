# This file extracts information and a list of battle events from verbose battle logs.

import active_model
import gamedata
import log_parser


log_filename = 'temp/example_logs/log1'

user = ''
log = ''
extensions = []
battle = active_model.Battle()


def set_user(name):
    global user
    user = name


def load_log():
    with open(log_filename) as f:
        global log
        log = f.read()


def update_battle():
    log_lines = log.splitlines()
    first_line_index = len(log_lines) - 1 - log_lines[::-1].index('Received extension response: joinbattle')
    parsed = log_parser.parse_battle('\n'.join(log_lines[first_line_index:]))
    players = [dict(), dict()]

    # Set up the battle by going through the joinbattle extension response.
    for obj in parsed[0]['objects']:
        if obj['_class_'] == 'com.cardhunter.battle.Battle':
            battle.scenario_name = obj['scenarioName']
            battle.scenario_display_name = obj['scenarioDisplayName']
            battle.game_type = obj['gameType']
            battle.audio_tag = obj['audioTag']
            battle.room_name = obj['roomName']
        elif obj['_class_'] == 'com.cardhunter.battle.Player':
            player = battle.players[obj['playerIndex']]
            player.name = obj['playerName']
            player.rating = obj['rating']
        elif obj['_class_'] == 'com.cardhunter.battle.ActorGroup':
            for enemy in battle.enemies():
                if not enemy.is_described():
                    enemy.name = obj['name']
                    enemy.set_archetype(obj['race'] + ' ' + obj['characterClass'])
                    break
        elif obj['_class_'] == 'com.cardhunter.battle.ActorInstance':
            for enemy in battle.enemies():
                if not enemy.is_described():
                    enemy.figure = obj['depiction']
                    # enemy.audio_key = obj['audioKey']
                    # enemy.x = obj['position.x']
                    # enemy.y = obj['position.y']
                    # enemy.fx = obj['facing.x']
                    # enemy.fy = obj['facing.y']
                    break

    # Create a list of "events".

    # Some other class will be able to deal with the list of events. We can just return the list.

