#!/usr/bin/env python3.6

import optimize
import gamedata


def main():
    gamedata.load()
    optimize.load()

    archetype = input('Archetype: ')
    print('Card Classes:\n ', '\n  '.join(sorted(optimize.get_card_classes().keys())))
    print()
    card_class_input = input('Optimize for: ')

    card_class_combo = dict()
    total_weight = 0
    for card_class_input in card_class_input.split(','):
        if '=' in card_class_input:
            name, weight = card_class_input.split('=')
            name = name.replace(':', '').strip()
            weight = float(weight.strip())
        else:
            name = card_class_input.replace(':', '').strip()
            weight = 1
        if ':' in card_class_input:
            card_class = {name: weight}
        else:
            card_class = optimize.get_card_class(name)
        for card in card_class:
            card_class_combo[card] = card_class_combo.get(card, 0) + weight * card_class[card]
        total_weight += weight
    for card in card_class_combo:
        card_class_combo[card] /= total_weight

    score, num_traits, optimum = optimize.find(archetype, card_class_combo)[0]
    print('\nTotal value: {}\nNumber of traits: {}\nAverage value: {}'.format(score, num_traits, score / (36 - num_traits)))
    print(', '.join(str(x) for x in optimum))
    print()
    for item in optimum:
        print(', '.join([str(card) for card in item.cards]), sep='')


if __name__ == '__main__':
    main()
