# This file extracts the relevant info from verbose battle logs.

import active_model
import gamedata
import log_parser


log_filename = 'temp/example_logs/log1'

user = ''
log = ''
extensions = []
battle = active_model.ActiveBattle()


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
    battle_meta = parsed[0]['objects']
    scenario_name = battle_meta['scenarioName'].value
    scenario_display_name = battle_meta['scenarioDisplayName'].value
    game_type = battle_meta['gameType'].value
    audio_tag = battle_meta['audioTag'].value
    room_name = battle_meta['roomName'].value

    # player_index = 0
    # enemy_race = enemy_role = enemy_name = ''
    # card_origin = card_type = ''
    # cownerp = cownerg = card_index = -1
    # card_infs = 0
    # for line in log_lines[first_line_index:]:
    #     if not battle.is_described():
    #         if '(utf_string) roomName: ' in line:
    #             battle.room_name = line.split('(utf_string) roomName: ')[1]
    #         elif '(utf_string) scenarioName: ' in line:
    #             battle.scenario_name = line.split('(utf_string) scenarioName: ')[1]
    #         elif '(utf_string) scenarioDisplayName: ' in line:
    #             battle.scenario_display_name = line.split('(utf_string) scenarioDisplayName: ')[1]
    #         elif '(utf_string) playerName: ' in line:
    #             player_name = line.split('(utf_string) playerName: ')[1]
    #             if player_name != user:
    #                 battle.enemy_name = player_name
    #                 battle.enemy_index = player_index
    #             player_index += 1
    #     elif not all(enemy.name for enemy in battle.enemies):
    #         if '(utf_string) characterClass: ' in line:
    #             enemy_role = line.split('(utf_string) characterClass: ')[1]
    #         elif '(utf_string) race: ' in line:
    #             enemy_race = line.split('(utf_string) race: ')[1]
    #         elif '(utf_string) name: ' in line:
    #             enemy_name = line.split('(utf_string) name: ')[1]
    #         elif '(utf_string) depiction: ' in line:
    #             for enemy in battle.enemies:
    #                 if enemy.archetype is None:
    #                     enemy.figure = line.split('(utf_string) depiction: ')[1]
    #                     enemy.set_archetype(enemy_race + ' ' + enemy_role)
    #                     enemy.name = enemy_name
    #                     enemy_race = ''
    #                     enemy_role = ''
    #                     enemy_name = ''
    #                     break
    #     else:
    #         if '(utf_string) origin: ' in line:
    #             card_origin = line.split('(utf_string) origin: ')[1]
    #             card_infs += 1
    #         elif '(int) cownerp: ' in line:
    #             cownerp = int(line.split('(int) cownerp: ')[1])
    #             card_infs += 1
    #         elif '(int) cownerg: ' in line:
    #             cownerg = int(line.split('(int) cownerg: ')[1])
    #             card_infs += 1
    #         elif '(int) card: ' in line:
    #             card_index = int(line.split('(int) card: ')[1])
    #             card_infs += 1
    #         elif '(utf_string) type: ' in line:
    #             temp_card_type = line.split('(utf_string) type: ')[1]
    #             if gamedata.is_card(temp_card_type):
    #                 card_type = temp_card_type
    #                 card_infs += 1
    #         if card_infs == 5:
    #             if cownerp == battle.enemy_index and gamedata.is_item(card_origin):
    #                 battle.enemies[cownerg].play_card(gamedata.get_card(card_type), gamedata.get_item(card_origin))
    #                 for enemy in battle.enemies:
    #                     print()
    #                     print(enemy)
    #                     print()
    #             card_origin = card_type = ''
    #             cownerp = cownerg = card_index = -1
    #             card_infs = 0

