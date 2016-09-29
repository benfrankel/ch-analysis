import gamedata
import log


log_filename = 'temp/example_logs/log1'
#gamedata.download()
gamedata.load()


while True:
    command = input().lower().replace(' ', '')

    if command in ('u', 'r'):
        log.load_log(log_filename)
        log.load_battle()
    if command in ('d', 'r'):
        for enemy in log.battle.enemy.team:
            print()
            print(enemy)
            print()
        print('Enemy =', log.battle.enemy.name, 'index', log.battle.enemy.index)
        print(log.battle.scenario_name, 'aka', log.battle.scenario_display_name)
        print(log.battle.room_name)
        print()
        print(log.battle.map)
        for i, event in enumerate(log.events):
            print(i, event)
