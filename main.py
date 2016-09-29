import gamedata
import events


log_filename = 'temp/example_logs/log1'
#gamedata.download()
gamedata.load()


while True:
    command = input().lower().replace(' ', '')

    if command in ('u', 'r'):
        events.reset()
        events.load_log(log_filename)
        events.load_battle()
    if command in ('d', 'r'):
        for enemy in events.battle.enemy.team:
            print()
            print(enemy)
            print()
        print('Enemy =', events.battle.enemy.name, 'index', events.battle.enemy.index)
        print(events.battle.scenario_name, 'aka', events.battle.scenario_display_name)
        print(events.battle.room_name)
        print()
        print(events.battle.map)
        for i, event in enumerate(events.events):
            print(i, event)
