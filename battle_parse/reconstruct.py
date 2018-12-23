# This file extracts information and a list of battle events from verbose battle logs

from tkinter import Tk
import re

from util import log_parse
from .extension import *
from .message import *
from . import model


# Load objects into scenario
def load_scenario(objs):
    scenario = model.Scenario()

    for obj in objs:
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

    return scenario


# Extract extension events
def extension_events(scenario, extensions):
    events = []
    player_turn = -1
    must_discard = [-1, -1]
    for ex in extensions:
        ex_name = ex.get('_NAME')
        event_type = ex.get('type')

        if ex_name != 'battleTimer' and (ex_name != 'battle' or event_type == 'done'):
            continue

        if ex_name == 'battleTimer':
            player_index = ex['playerIndex']
            start = ex['start']
            remaining = ex['timeRemaining']

            if start:
                player_turn = player_index
            else:
                player_turn = -1

            events.append(ExTimer(-1, player_index, start, remaining))

        elif event_type == 'deckPeeksSent':
            events.append(ExDeckPeek(player_turn))

        elif event_type == 'handPeeksSent':
            events.append(ExHandPeek(player_turn))

        elif event_type == 'deckPeeks':
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
                events.append(ExCardDraw(player_turn, original_player_index, original_group_index, player_index,
                                         group_index, card_index, item_name, card_name))

        elif event_type == 'handPeeks':
            # For every card in the peeks array, extract its info and append an event for it
            for info in ex['HP']['peeks']:
                original_player_index = info['cownerp']
                original_group_index = info['cownerg']
                card_index = info['card']
                item_name = info['origin']
                card_name = info['type']
                player_index = info['owner']
                group_index = info['group']
                events.append(ExCardReveal(player_turn, original_player_index, original_group_index, player_index,
                                           group_index, card_index, item_name, card_name))

        elif event_type == 'action':
            # For every card in the peeks array, extract its info and append an event for it
            for info in ex['HP']['peeks']:
                original_player_index = info['cownerp']
                original_group_index = info['cownerg']
                card_index = info['card']
                item_name = info['origin']
                card_name = info['type']
                player_index = info['owner']
                group_index = info['group']
                events.append(ExCardPlay(player_turn, original_player_index, original_group_index, player_index,
                                         group_index, card_index, item_name, card_name))

                if 'TARP' in ex:
                    target_player_indices = ex['TARP']
                    target_group_indices = ex['TARG']
                    events.append(ExSelectTarget(player_turn, target_player_indices, target_group_indices))

        elif event_type == 'selectCard':
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
                    events.append(ExCardDiscard(player_turn, original_player_index, original_group_index, player_index,
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
                    events.append(ExCardDiscard(player_turn, original_player_index, original_group_index, player_index,
                                                group_index, card_index, item_name, card_name))

        # elif event_type == 'selectCards':
        #     if 'SELP' in ex:
        #         selected_player_indices = ex['SELP']
        #         selected_group_indices = ex['SELG']
        #         selected_card_indices = ex['SELCC']
        #         for i in range(len(selected_player_indices)):
        #             events.append(ExSelectEvent(player_turn, selected_player_indices[i], selected_group_indices[i],
        #                                         selected_card_indices[i]))

        elif event_type == 'mustDiscard':
            # Remember who must discard
            player_index = ex['PUI']
            group_index = ex['ACTG']
            must_discard[0] = player_index
            must_discard[1] = group_index
            events.append(ExMustDiscard(player_turn, player_index, group_index))

        elif event_type == 'noMoreDiscards':
            events.append(ExNoDiscards(player_turn))

        elif event_type == 'hasTrait':
            player_index = ex['PUI']
            events.append(ExMustTrait(player_turn, player_index))

        elif event_type == 'noMoreTraits':
            events.append(ExNoTraits(player_turn))

        elif event_type in ('triggerFail', 'triggerSucceed') and 'TCLOC' in ex:
            die_roll = ex['TROLL']
            required_roll = ex['TTHRESH']
            hard_to_block = ex['TPEN']
            easy_to_block = ex['TBON']
            location = ex['TCLOC']
            
            if location == 0:
                player_index = ex['PUI']
                group_index = ex['ACTG']
                card_index = ex['ACTC']
                events.append(ExTriggerHand(player_turn, die_roll, required_roll, hard_to_block, easy_to_block, player_index,
                                            group_index, card_index))

            elif location == 1:
                player_index = ex['PUI']
                group_index = ex['ACTG']
                events.append(ExTriggerAttachment(player_turn, die_roll, required_roll, hard_to_block, easy_to_block,
                                                  player_index, group_index))

            elif location == 2:
                x = ex['TARX']
                y = ex['TARY']
                events.append(ExTriggerTerrain(player_turn, die_roll, required_roll, hard_to_block, easy_to_block, x, y))

        elif event_type == 'target':
            target_player_indices = ex['TARP']
            target_group_indices = ex['TARG']
            events.append(ExSelectTarget(player_turn, target_player_indices, target_group_indices))

        elif event_type == 'selectSquare':
            x = ex['TARX']
            y = ex['TARY']
            fx = ex['TARFX']
            fy = ex['TARFY']
            events.append(ExSelectSquare(player_turn, x, y, fx, fy))

        elif event_type == 'genRand':
            rands = ex['RAND']
            events.append(ExRNG(player_turn, rands))

        elif event_type == 'pass':
            events.append(ExPass(player_turn))

        elif event_type == 'forceLoss':
            events.append(ExResign(player_turn))

        else:
            print('Ignored:', ex)

    return events


# Extract message events
def message_events(scenario, messages):
    events = []

    p0 = re.escape(scenario.players[0].name)
    p1 = re.escape(scenario.players[1].name)
    player = '({}|{})'.format(p0, p1)
    p0g0 = re.escape(scenario.players[0].groups[0].name)
    p0g1 = re.escape(scenario.players[0].groups[1].name)
    p0g2 = re.escape(scenario.players[0].groups[2].name)
    p1g0 = re.escape(scenario.players[1].groups[0].name)
    p1g1 = re.escape(scenario.players[1].groups[1].name)
    p1g2 = re.escape(scenario.players[1].groups[2].name)
    group = '({}|{}|{}|{}|{}|{})'.format(p0g0, p0g1, p0g2, p1g0, p1g1, p1g2)

    start_round = re.compile(r'^Starting round (\d+)$')
    end_round = re.compile(r'^Turn Complete$')
    scoring_phase = re.compile(r'^Scoring Phase: initiated$')
    discard_phase = re.compile(r'^Discard Phase: initiated$')
    defeat = re.compile(r'^{} was defeated$'.format(player))
    draw = re.compile(r'^{} drew (.+) for {}$'.format(player, group))
    must_trait = re.compile(r'^{} must play a Trait$'.format(player))
    must_target = re.compile(r'^Participant {} must select targets$'.format(player))
    attach_trait = re.compile(r'^Attaching (.+) to {}$'.format(group))
    detach_trait = re.compile(r'^Detaching and discarding (.+) from {}$'.format(group))
    attach_terrain = re.compile(r'^Attaching (.+) to \((\d+), (\d+)\)$')
    active_player = re.compile(r'^The active player is now {}$'.format(player))
    passed = re.compile(r'^{} passed\.$'.format(player))
    ended_round = re.compile(r'^{} ended the round.$'.format(player))
    cancelling = re.compile(r'^Action: (.+) is invalid - cancelling$')
    cancelled = re.compile(r'^(.+) was cancelled.$')
    damage = re.compile(r'^{} took (\d+) damage$'.format(group))
    heal = re.compile(r'^{} healed (\d+)$'.format(group))
    die = re.compile(r'^{} died$'.format(group))
    block = re.compile(r'^{}, health = (\d+) \(pi:(\d), gi:(\d), ai:(\d)\)  blocks (.+)$'.format(group))
    autoselect = re.compile(r'^SeeverSelectCardsCommand:: selected card (.+)$')

    for m in messages:
        event = m.get('Event')
        msg = m.get('Msg')

        if event is not None:
            if event == 'StartGame':
                events.append(MsgStartGame())

            elif event == 'GameOver':
                events.append(MsgEndGame())

            elif event == 'Attachment Phase Initiated':
                events.append(MsgAttachmentPhase())

            elif event == 'Draw Phase Initiated':
                events.append(MsgDrawPhase())

            elif event == 'Action Phase Initiated':
                events.append(MsgActionPhase())

            elif event == 'PlayAction':
                targets = m['Targets']
                if targets == '':
                    targets = []
                elif isinstance(targets, str):
                    targets = [targets]
                group = m['Instigator']
                card = m['Action']
                events.append(MsgCardPlay(group, card, targets))

            elif event == 'Move':
                start_facing = m['StartFacing']
                end_facing = m['EndFacing']
                start = m['Origin']
                end = m['Destination']
                group = m['Actor']
                player = m['Player']
                events.append(MsgMove(player, group, start, end, start_facing, end_facing))

            elif event.startswith('Trigger'):
                success = event.endswith('Succeed')
                group = m['TriggeringActor']
                card = m['Trigger']
                target = m['AffectedActors']
                loc = m['TriggerLocation']
                cause = m['TriggerType']
                if loc == 'SquareAttachment':
                    events.append(MsgTriggerTerrain(group, card, target, success, cause))
                elif loc == 'ActorAttachment':
                    events.append(MsgTriggerTrait(group, card, target, success, cause))
                else:
                    events.append(MsgTriggerInHand(group, card, target, success, cause))

            elif event == 'Needs to discard a card':
                group = m['Group']
                events.append(MsgMustDiscard(group))

            elif event == 'Discard':
                card = m['Card']
                group = m['Group']
                events.append(MsgDiscard(group, card))

            elif event == 'SelectCardRequired':
                player = m['Participant']
                player_id = m['PlayerID']
                options = m['Selections']
                choice_type = m['ChoiceType']  # TODO: What can this be?
                events.append(MsgMustSelect(player, options))

            elif event == 'SelectCard':
                card = m['Selection']
                player = m['Participant']
                events.append(MsgSelect(player, card))

            elif event == 'AttachmentExpired':
                card = m['Attachment']
                loc = m['AttachedTo']
                if isinstance(loc, list):
                    square = loc
                    events.append(MsgDetachTerrain(square, card))
                else:
                    group = loc
                    events.append(MsgDetachTrait(group, card))

            elif event == 'startTimer':
                player_index = m['PlayerIndex']
                remaining = m['Remaining']
                events.append(MsgStartTimer(player_index, remaining))

            elif event == 'stopTimer':
                player_index = m['PlayerIndex']
                remaining = m['Remaining']
                events.append(MsgStopTimer(player_index, remaining))

            else:
                print('Ignored:', m)

        elif msg is not None:
            if start_round.fullmatch(msg):
                match = start_round.fullmatch(msg)
                round_ = int(match.groups()[0])
                events.append(MsgStartRound(round_))

            elif end_round.fullmatch(msg):
                events.append(MsgEndRound())

            elif scoring_phase.fullmatch(msg):
                events.append(MsgScoringPhase())

            elif discard_phase.fullmatch(msg):
                events.append(MsgDiscardPhase())

            elif defeat.fullmatch(msg):
                match = defeat.fullmatch(msg)
                player = match.groups()[0]
                events.append(MsgDefeat(player))

            elif draw.fullmatch(msg):
                match = draw.fullmatch(msg)
                player = match.groups()[0]
                card = match.groups()[1]
                group = match.groups()[2]
                if card == 'a card':
                    events.append(MsgHiddenDraw(player, group))
                else:
                    events.append(MsgCardDraw(player, group, card))

            elif must_trait.fullmatch(msg):
                match = must_trait.fullmatch(msg)
                player = match.groups()[0]
                events.append(MsgMustTrait(player))

            elif must_target.fullmatch(msg):
                match = must_target.fullmatch(msg)
                player = match.groups()[0]
                events.append(MsgMustTarget(player))

            elif attach_trait.fullmatch(msg):
                match = attach_trait.fullmatch(msg)
                card = match.groups()[0]
                group = match.groups()[1]
                events.append(MsgAttachTrait(group, card))

            elif detach_trait.fullmatch(msg):
                match = detach_trait.fullmatch(msg)
                card = match.groups()[0]
                group = match.groups()[1]
                events.append(MsgDetachTrait(group, card))

            elif attach_terrain.fullmatch(msg):
                match = attach_terrain.fullmatch(msg)
                card = match.groups()[0]
                x = int(match.groups()[1])
                y = int(match.groups()[2])
                events.append(MsgAttachTerrain([x, y], card))

            elif active_player.fullmatch(msg):
                match = active_player.fullmatch(msg)
                player = match.groups()[0]
                events.append(MsgPlayerTurn(player))

            elif passed.fullmatch(msg):
                match = passed.fullmatch(msg)
                player = match.groups()[0]
                events.append(MsgPass(player))

            elif ended_round.fullmatch(msg):
                match = ended_round.fullmatch(msg)
                player = match.groups()[0]
                events.append(MsgPass(player))

            elif cancelling.fullmatch(msg):
                match = cancelling.fullmatch(msg)
                card = match.groups()[0]
                events.append(MsgCancelAction(card))

            elif cancelled.fullmatch(msg):
                match = cancelled.fullmatch(msg)
                card = match.groups()[0]
                events.append(MsgStopCard(card))

            elif damage.fullmatch(msg):
                match = damage.fullmatch(msg)
                group = match.groups()[0]
                hp = int(match.groups()[1])
                events.append(MsgDamage(group, hp))

            elif heal.fullmatch(msg):
                match = heal.fullmatch(msg)
                group = match.groups()[0]
                hp = int(match.groups()[1])
                events.append(MsgHeal(group, hp))

            elif die.fullmatch(msg):
                match = die.fullmatch(msg)
                group = match.groups()[0]
                events.append(MsgDeath(group))

            elif block.fullmatch(msg):
                match = block.fullmatch(msg)
                group = match.groups()[0]
                hp = int(match.groups()[1])
                player_index = int(match.groups()[2])
                group_index = int(match.groups()[3])
                actor_index = int(match.groups()[4])
                card = match.groups()[5]
                events.append(MsgBlock(player_index, group_index, card))
                events.append(MsgHealth(player_index, group_index, hp))

            elif autoselect.fullmatch(msg):
                match = autoselect.fullmatch(msg)
                card = match.groups()[0]
                events.append(MsgAutoselect(card))

            else:
                print('Ignored:', m)

        else:
            print('Ignored:', m)

    return events


# Form higher-level events
def refine_events(scenario, ex_events, msg_events):
    # TODO

    for event in ex_events:
        pass
        # print(event)

    for event in msg_events:
        pass
        # print(event)

    return ex_events


# Use the log text to construct a sequence of events that can be fed into a Battle
def load_battle(filename=None):
    # Load log contents into memory
    if filename is None:
        root = Tk()
        root.withdraw()
        try:
            log = root.clipboard_get()
        except:
            return None, None
    else:
        with open(filename) as f:
            log = f.read()

    # Find the most recent joinbattle
    log_lines = log.splitlines()
    try:
        first_line_index = len(log_lines) - 1 - log_lines[::-1].index('Received extension response: joinbattle')
    except:
        return None, None

    # Parse battle logs
    extensions, messages = log_parse.parse_battle('\n'.join(log_lines[first_line_index:]))
    joinbattle, extensions = extensions[0], extensions[1:]

    # Load objects into scenario
    scenario = load_scenario(joinbattle['objects'])

    if not scenario.is_described():
        pass  # Scenario not completely started

    # Extract extension events
    ex_events = extension_events(scenario, extensions)

    # Extract message events
    msg_events = message_events(scenario, messages)

    # Interpolate and extrapolate to form higher-level events
    events = refine_events(scenario, ex_events, msg_events)

    return events, scenario
