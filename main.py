#!/usr/bin/env python3.6

import gamedata

from battle_parse import reconstruct


log_filename = 'info/example_logs/log1'


def battle_test():
    event_list = []
    scenario = None

    while True:
        print('Commands: (u)pdate, (r)efresh, (s)how, (d)ownload')

        command = input().lower().replace(' ', '')

        if command in "ur":
            event_list, scenario = reconstruct.load_battle()
            if not event_list:
                event_list, scenario = reconstruct.load_battle(log_filename)
        if command in "sr":
            print('> TITLE')
            print(scenario.name, 'aka', scenario.display_name)
            print(scenario.room_name)
            print('\n')
            print('> PLAYERS')
            print('User is {}, index {}'.format(scenario.user.name, scenario.user.index))
            print('Enemy is {}, index {}'.format(scenario.enemy.name, scenario.enemy.index))
            print('\n')
            print('> CHARACTERS')
            for i, enemy in enumerate(scenario.enemy.groups):
                print(i, enemy)
                print()
            print()
            print('> MAP')
            print(scenario.map)
            print('\n')
            print('> EVENTS')
            for i, event in enumerate(event_list):
                print(i, event)
        if command == 'd':
            gamedata.download()
            gamedata.load()

        print()


battle_test()
