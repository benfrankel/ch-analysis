from django.shortcuts import render
import optimize
import gamedata


def optimize_for(archetype, values):
    card_pack_combo = dict()
    total_weight = 0
    for card_pack_input in values.split(','):
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

    cards = '\n'.join(', '.join(str(card) for card in item.cards) for item in optimum)

    return (
        f'Total value: {score}\n'
        f'Number of traits: {num_traits}\n'
        f'Average value: {score / (36 - num_traits)}\n'
        f'{", ".join(str(x) for x in optimum)}\n'
        f'\n'
        f'{cards}'
    )


def index(request):
    gamedata.load()
    optimize.load()
    context = {'card_packs': sorted(optimize.get_card_packs().keys())}
    if request.POST:
        archetype = f'{request.POST["race"]} {request.POST["class"]}'
        values = request.POST['card-values']
        context['result'] = optimize_for(archetype, values)
    return render(request, 'optimize/index.html', context)
