import gamedata
import reconstruct


log_filename = 'temp/example_logs/log1'
# gamedata.download()
gamedata.load()


while True:
    event_list = []
    command = input().lower().replace(' ', '')

    if command in ('u', 'r'):
        event_list, battle = reconstruct.load_battle()
        if not event_list:
            event_list, battle = reconstruct.load_battle(log_filename)
    if command in ('d', 'r'):
        for enemy in battle.enemy.groups:
            print()
            print(enemy)
            print()
        print('Enemy =', battle.enemy.name, 'index', battle.enemy.index)
        print(battle.scenario_name, 'aka', battle.scenario_display_name)
        print(battle.room_name)
        print()
        print(battle.map)
        for i, event in enumerate(event_list):
            print(i, event)
