import gamedata
import log
import log_parser


log_filename = 'temp/example_logs/log2'
gamedata.load()


while True:
    command = input().lower().replace(' ', '')

    if command in ('u', 'r'):
        log.load_log(log_filename)
        log.update_battle()
    if command in ('d', 'r'):
        for enemy in log.battle.enemy.team:
            print()
            print(enemy)
            print()
        print(log.battle.enemy.name)
        print(log.battle.enemy.index)
        print(log.battle.scenario_name)
        print(log.battle.scenario_display_name)
        print(log.battle.room_name)
        print(log.battle.map)
