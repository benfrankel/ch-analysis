# This file extracts information and a list of battle events from verbose battle logs

from tkinter import Tk

from util import log_parse
from .event import *
from . import model


# Use the log text to construct a sequence of events that can be fed into a Battle
def load_battle(filename=''):
    events = []
    scenario = model.Scenario()

    def update_scenario(event):
        events.append(event)
        scenario.update(event)

    # Load log contents into memory
    if filename == '':
        root = Tk()
        root.withdraw()
        try:
            log = root.clipboard_get()
        except:
            return events, scenario
        if 'Received extension response: joinbattle' not in log:
            return events, scenario
    else:
        with open(filename) as f:
            log = f.read()

    # Find the most recent joinbattle parse the battle
    log_lines = log.splitlines()
    first_line_index = len(log_lines) - 1 - log_lines[::-1].index('Received extension response: joinbattle')
    extensions, messages = log_parse.parse_battle('\n'.join(log_lines[first_line_index:]))

    # Set up the battle by extracting all relevant info from joinbattle
    for obj in extensions[0]['objects']:
        if obj['_class_'] == 'com.cardhunter.battle.Battle':
            scenario.name = obj['scenarioName']
            scenario.display_name = obj['scenarioDisplayName']
            scenario.game_type = obj['gameType']
            scenario.audio_tag = obj['audioTag']
            scenario.room_name = obj['roomName']

        elif obj['_class_'] == 'com.cardhunter.battle.Player':
            player_index = obj['playerIndex']
            player = scenario.players[player_index]
            player.name = obj['playerName']
            player.rating = obj['rating']

        elif obj['_class_'] == 'com.cardhunter.battle.Square':
            scenario.map.add_square(obj['location.x'], obj['location.y'], obj['imageFlipX'], obj['imageFlipY'],
                                    obj['imageName'], obj['terrain'])

        elif obj['_class_'] == 'com.cardhunter.battle.Doodad':
            scenario.map.add_doodad(obj['displayPosition.x'], obj['displayPosition.y'], obj['imageFlipX'],
                                    obj['imageFlipY'], obj['imageName'], obj['marker'])

        elif obj['_class_'] == 'com.cardhunter.battle.ActorGroup':
            for group in scenario.players[0].groups + scenario.players[1].groups:
                if not group.is_described():
                    group.name = obj['name']
                    group.set_archetype(' '.join([obj['race'], obj['characterClass']]))
                    break

        elif obj['_class_'] == 'com.cardhunter.battle.ActorInstance':
            for group in scenario.players[0].groups + scenario.players[1].groups:
                if not group.is_described():
                    group.figure = obj['depiction']
                    group.audio_key = obj['audioKey']
                    group.x = obj['location.x']
                    group.y = obj['location.y']
                    group.fx = obj['facing.x']
                    group.fy = obj['facing.y']
                    break

    if not scenario.is_described():
        pass  # Scenario not completely started

    # Figure out who the enemy is and construct a sequence of events
    player_turn = 0
    must_discard = [-1, -1]
    for ex, prev in zip(extensions[1:], extensions):
        print()
        print(ex)

        ex_name = ex.get('_NAME')
        ex_type = ex.get('type')

        if ex_name == 'battleTimer':
            player_index = ex['playerIndex']
            switch_timer = ex['start']
            if switch_timer:
                player_turn = player_index

        elif ex_name != 'battle':
            continue

        elif ex_type == 'deckPeeksSent' and ('type' not in prev or prev['type'] != 'deckPeeks'):
            update_scenario(HiddenDraw(player_turn))

        elif ex_type == 'deckPeeks':
            # If the user is still unknown, use this deckPeeks to determine who it is
            if scenario.user is None:
                scenario.set_user(ex['SENDID'][0])

            # For every card in the peeks array, extract its info and append an event for it
            for info in ex['DP']['peeks']:
                original_player_index = info['cownerp']
                original_group_index = info['cownerg']
                card_index = info['card']
                item_name = info['origin']
                card_name = info['type']
                player_index = info['owner']
                group_index = info['group']

                update_scenario(CardDraw(player_turn, original_player_index, original_group_index, player_index,
                                         group_index, card_index, item_name, card_name))

        elif ex_type == 'handPeeks':
            # For every card in the peeks array, extract its info and append an event for it
            for info in ex['HP']['peeks']:
                original_player_index = info['cownerp']
                original_group_index = info['cownerg']
                card_index = info['card']
                item_name = info['origin']
                card_name = info['type']
                player_index = info['owner']
                group_index = info['group']

                update_scenario(CardReveal(player_turn, original_player_index, original_group_index, player_index,
                                           group_index, card_index, item_name, card_name))

        elif ex_type == 'action':
            # For every card in the peeks array, extract its info and append an event for it
            for info in ex['HP']['peeks']:
                original_player_index = info['cownerp']
                original_group_index = info['cownerg']
                card_index = info['card']
                item_name = info['origin']
                card_name = info['type']
                player_index = info['owner']
                group_index = info['group']

                update_scenario(CardPlay(player_turn, original_player_index, original_group_index, player_index,
                                         group_index, card_index, item_name, card_name))

                if 'TARP' in ex:
                    target_player_indices = ex['TARP']
                    target_group_indices = ex['TARG']

                    update_scenario(SelectTarget(player_turn, target_player_indices, target_group_indices))

        elif ex_type == 'selectCard':
            # Discard during round
            if 'HP' in ex:
                for info in ex['HP']['peeks']:
                    original_player_index = info['cownerp']
                    original_group_index = info['cownerg']
                    card_index = info['card']
                    item_name = info['origin']
                    card_name = info['type']
                    player_index = info['owner']
                    group_index = info['group']

                    update_scenario(CardDiscard(player_turn, original_player_index, original_group_index, player_index,
                                                group_index, card_index, item_name, card_name))

            # Discard at end of round
            else:
                player_index = must_discard[0]
                group_index = must_discard[1]
                card_index = ex['sel']

                try:
                    card = scenario.players[player_index].groups[group_index].hand[card_index]
                    original_player_index = card.original_player_index
                    original_group_index = card.original_group_index
                    item_name = card.item_name
                    card_name = card.card_name
                except:
                    pass
                else:
                    update_scenario(CardDiscard(player_turn, original_player_index, original_group_index, player_index,
                                                group_index, card_index, item_name, card_name))

        # elif ex_type == 'selectCards':
        #     if 'SELP' in ex:
        #         selected_player_indices = ex['SELP']
        #         selected_group_indices = ex['SELG']
        #         selected_card_indices = ex['SELCC']
        #         for i in range(len(selected_player_indices)):
        #             update_scenario(SelectEvent(player_turn, selected_player_indices[i], selected_group_indices[i],
        #                                       selected_card_indices[i]))

        elif ex_type == 'mustDiscard':
            # Remember who must discard
            player_index = ex['PUI']
            group_index = ex['ACTG']

            must_discard[0] = player_index
            must_discard[1] = group_index

            update_scenario(MustDiscard(player_turn, player_index, group_index))

        elif ex_type == 'noMoreDiscards':
            update_scenario(NoDiscards(player_turn))

        elif ex_type == 'hasTrait':
            player_index = ex['PUI']

            update_scenario(MustPlayTrait(player_turn, player_index))

        elif ex_type == 'noMoreTraits':
            update_scenario(NoTraits(player_turn))

        elif ex_type in ('triggerFail', 'triggerSucceed') and 'TCLOC' in ex:
            die_roll = ex['TROLL']
            required_roll = ex['TTHRESH']
            hard_to_block = ex['TPEN']
            easy_to_block = ex['TBON']
            location = ex['TCLOC']

            if location == 0:
                player_index = ex['PUI']
                group_index = ex['ACTG']
                card_index = ex['ACTC']

                update_scenario(TriggerHand(player_turn, die_roll, required_roll, hard_to_block, easy_to_block, player_index,
                                            group_index, card_index))

            elif location == 1:
                player_index = ex['PUI']
                group_index = ex['ACTG']

                update_scenario(TriggerAttachment(player_turn, die_roll, required_roll, hard_to_block, easy_to_block,
                                                  player_index, group_index))

            elif location == 2:
                x = ex['TARX']
                y = ex['TARY']

                update_scenario(TriggerTerrain(player_turn, die_roll, required_roll, hard_to_block, easy_to_block, x, y))

        elif ex_type == 'target':
            target_player_indices = ex['TARP']
            target_group_indices = ex['TARG']

            update_scenario(SelectTarget(player_turn, target_player_indices, target_group_indices))

        elif ex_type == 'selectSquare':
            x = ex['TARX']
            y = ex['TARY']
            fx = ex['TARFX']
            fy = ex['TARFY']

            update_scenario(SelectSquare(player_turn, x, y, fx, fy))

        elif ex_type == 'genRand':
            rands = ex['RAND']

            update_scenario(RNG(player_turn, rands))

        elif ex_type == 'pass':
            update_scenario(Pass(player_turn))

        else:
            print('    | Ignored')

    return events, scenario
