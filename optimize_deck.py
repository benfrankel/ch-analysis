#!/usr/bin/env python3.6

import optimize

import gamedata


def main():
    gamedata.load()
    optimize.load()

    archetype = input('Archetype: ')
    print('Card Classes:\n ', '\n  '.join(sorted(optimize.get_card_packs().keys())))
    print()
    card_pack_input = input('Optimize for: ')

    card_pack_combo = dict()
    total_weight = 0
    for card_pack_input in card_pack_input.split(','):
        if '=' in card_pack_input:
            name, weight = card_pack_input.split('=')
            name = name.replace(':', '').strip()
            weight = float(weight.strip())
        else:
            name = card_pack_input.replace(':', '').strip()
            weight = 1
        if ':' in card_pack_input:
            card_pack = {name: weight}
        else:
            card_pack = optimize.get_card_pack(name)
        for card in card_pack:
            card_pack_combo[card] = card_pack_combo.get(card, 0) + weight * card_pack[card]
        total_weight += weight
    for card in card_pack_combo:
        card_pack_combo[card] /= total_weight

    score, num_traits, optimum = optimize.find(archetype, card_pack_combo)[0]
    print('\nTotal value: {}\nNumber of traits: {}\nAverage value: {}'.format(score, num_traits, score / (36 - num_traits)))
    print(', '.join(str(x) for x in optimum))
    print()
    for item in optimum:
        print(', '.join([str(card) for card in item.cards]), sep='')


if __name__ == '__main__':
    main()
