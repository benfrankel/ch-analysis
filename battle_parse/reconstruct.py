# This file extracts information and a list of battle events from verbose battle logs

from tkinter import Tk
import re

from util import log_parse
from .event import *
from . import model


# Load objects into battle
# TODO: Support player with multiple participants (party)
# TODO: Support quick draw (?)
# TODO: Support groups with multiple actors
def load_battle_objects(objs):
    battle = model.Battle()
    board = battle.board
    group_at = {}
    actor_at = {}

    for i, obj in enumerate(objs):
        cls = obj['_class_']
        
        if cls.endswith('.Battle'):
            battle.scenario_name = obj['scenarioName']
            battle.display_name = obj['scenarioDisplayName']
            battle.room_name = obj['roomName']
            battle.room_id = obj['roomID']
            battle.time_limit = obj['timeLimit']  # In an adventure this was -60?
            battle.use_draw_limit = obj['enforceDrawLimit']
            battle.game_type = obj['gameType']  # TODO: What does this represent?
            battle.audio_tag = obj['audioTag']
            battle.respawn_period = obj['respawnPeriod']
            battle.win_on_all_dead = obj['forceWinWhenAllDead']
            battle.current_turn = obj['activePlayer']
            battle.current_round = obj['turnNumber']
            battle.game_over = obj['gameOver']
            # TODO: obj['nextFirstPlayerIndex']?
            # TODO: obj['awaitingInstruction']?
            # TODO: obj['adventureName']?
            # TODO: obj['respawnFilters']?
            # TODO: Is obj['questIndex'] used for quest adventures?
            # TODO: When would obj['playerDamageMultiplier'] not be 1?
            # TODO: obj['musicTag']?
            # TODO: What is obj['commands']?
            # TODO: What is obj['commandInsertionPoint']?
            # TODO: Is obj['initialHelpDoc'] related to GM narration?
            # TODO: Is obj['instructions'] related to GM narration?
            # TODO: Looks like obj['leagueID'] is -1 when not a league?
            # TODO: What is obj['scriptConditions']?

        elif cls.endswith('.Board'):
            board.w = obj['size.x']
            board.h = obj['size.y']

        elif cls.endswith('.Square'):
            board.add_square(
                x=obj['location.x'],
                y=obj['location.y'],
                flip_x=obj['imageFlipX'],
                flip_y=obj['imageFlipY'],
                image_name=obj['imageName'],
                terrain=obj['terrain'],
            )

        elif cls.endswith('.Doodad'):
            board.add_doodad(
                x=obj['displayPosition.x'],
                y=obj['displayPosition.y'],
                flip_x=obj['imageFlipX'],
                flip_y=obj['imageFlipY'],
                image_name=obj['imageName'],
                marker=obj['marker'],  # TODO: What does this represent? Only on PlayerNDeadFigureM?
            )

        elif cls.endswith('.Player'):
            player_index = obj['playerIndex']
            player = battle.players[player_index]

            for idx in obj['actorGroups']:
                group_at[idx] = player.add_group()
            
            player.name = obj['playerName']
            player.player_id = obj['playerID']  # TODO: -1 for NPC
            player.user_id = obj['userID']  # TODO: -1 for NPC
            player.is_npc = obj['isNPC']
            player.rating = obj['rating']  # TODO: -1 for NPC
            player.draw_limit = obj['drawLimit']  # TODO: Is this -1 when there is no draw limit?
            player.cards_drawn = obj['cardsDrawnThisRound']
            player.stars_needed = obj['winningScore']
            player.stars = obj['score']
            # TODO: obj['moveStartTime']?
            # TODO: obj['isParty']?
            # TODO: Is obj['side'] == obj['playerIndex'] always?
            # TODO: obj['passingAsOf']?
            # TODO: obj['defeated']?
            # TODO: obj['active']?
            # TODO: obj['quickDraw']?
            # TODO: Is obj['activeParticipantIndex'] the currently active participant in the party?
            # TODO: obj['initiativeParticipantIndex']?

        elif cls.endswith('.ActorGroup'):
            group = group_at[i]

            for j in obj['actors']:
                actor_at[j] = group.add_actor()
                
            group.name = obj['name']
            group.display_name = obj['displayName']
            group.set_archetype(
                archetype_name='{} {}'.format(obj['race'], obj['characterClass']),
            )
            group.base_ap = obj['actionPoints']
            group.draws_per_actor = obj['drawsPerActor']
            group.draw_limit = obj['drawLimit']
            # TODO: obj['cardsDrawnThisRound']?
            # TODO: When would obj['canScore'] be false?
            # TODO: obj['racePrefix']?
            # TODO: Is obj['moveCard'] necessary? Yes, what if it's a Goblin or something?
            # TODO: When would obj['cardRetainAllowance'] not be -1 and what does that mean?

        elif cls.endswith('.ActorInstance'):
            actor = actor_at[i]
            actor.name = obj['name']
            actor.figure = obj['depiction']
            actor.figure_size = obj['size']
            actor.audio_key = obj['audioKey']
            actor.star_value = obj['scoreForKilling']
            actor.max_hp = obj['maxHealth']
            actor.hp = obj['health']
            actor.ap = obj['actionPoints']    # TODO: -1 for infinite
            actor.x = obj['location.x']
            actor.y = obj['location.y']
            actor.fx = obj['facing.x']
            actor.fy = obj['facing.y']
            # TODO: obj['terrainEffectApplied']?
            # TODO: obj['swapDepiction']?
            # TODO: obj['attachedCards']?

        else:
            print('Ignored:', obj)
            # TODO: Handle .Hand
            # TODO: Handle .CardInstance
            # TODO: Handle .DiscardPile (?)
            # TODO: Handle .DeckInstance

    return battle


# Extract extension events
def extension_events(battle, extensions):
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
                events.append(ExStartTimer(
                    -1,
                    player_index,
                    remaining,
                ))
                
            else:
                player_turn = -1
                events.append(ExPauseTimer(
                    -1,
                    player_index,
                    remaining,
                ))

        elif event_type == 'deckPeeksSent':
            events.append(ExDeckPeek(
                player_turn,
            ))

        elif event_type == 'handPeeksSent':
            events.append(ExHandPeek(
                player_turn,
            ))

        elif event_type == 'deckPeeks':
            # If user is still unknown, use this deckPeeks to determine who it is
            if battle.user is None:
                user = ex['SENDID'][0]
                battle.set_user(user)

            # For every card in the peeks array, extract its info and append an event for it
            deck_peeks = ex['DP']['peeks']
            for peek in deck_peeks:
                events.append(ExCardDraw(
                    player_turn,
                    player_index=peek['owner'],
                    group_index=peek['group'],
                    card_index=peek['card'],
                    original_player_index=peek['cownerp'],
                    original_group_index=peek['cownerg'],
                    item_name=peek['origin'],
                    card_name=peek['type'],
                ))

        elif event_type == 'handPeeks':
            # For every card in the peeks array, extract its info and append an event for it
            hand_peeks = ex['HP']['peeks']
            for peek in hand_peeks:
                events.append(ExCardReveal(
                    player_turn,
                    player_index=peek['owner'],
                    group_index=peek['group'],
                    card_index=peek['card'],
                    original_player_index=peek['cownerp'],
                    original_group_index=peek['cownerg'],
                    item_name=peek['origin'],
                    card_name=peek['type'],
                ))

        elif event_type == 'action':
            # For every card in the peeks array, extract its info and append an event for it
            hand_peeks = ex['HP']['peeks']
            for peek in hand_peeks:
                events.append(ExCardPlay(
                    player_turn,
                    player_index=peek['owner'],
                    group_index=peek['group'],
                    card_index=peek['card'],
                    original_player_index=peek['cownerp'],
                    original_group_index=peek['cownerg'],
                    item_name=peek['origin'],
                    card_name=peek['type'],
                ))

                if 'TARP' in ex:
                    events.append(ExSelectTarget(
                        player_turn,
                        target_player_indices=ex['TARP'],
                        target_group_indices=ex['TARG'],
                    ))

        elif event_type == 'selectCard':
            # Discard during round
            if 'HP' in ex:
                hand_peeks = ex['HP']['peeks']
                for peek in hand_peeks:
                    events.append(ExCardDiscard(
                        player_turn,
                        player_index=peek['owner'],
                        group_index=peek['group'],
                        card_index=peek['card'],
                        original_player_index=peek['cownerp'],
                        original_group_index=peek['cownerg'],
                        item_name=peek['origin'],
                        card_name=peek['type'],
                    ))

            # Discard at end of round
            else:
                player_index = must_discard[0]
                group_index = must_discard[1]
                card_index = ex['sel']

                try:
                    card = battle.players[player_index].groups[group_index].hand[card_index]
                except:
                    pass
                else:
                    events.append(ExCardDiscard(
                        player_turn,
                        player_index,
                        group_index,
                        card_index,
                        original_player_index=card.original_player_index,
                        original_group_index=card.original_group_index,
                        item_name=card.item_name,
                        card_name=card.card_name,
                    ))

        # elif event_type == 'selectCards':
        #     if 'SELP' in ex:
        #         selected_player_indices = ex['SELP']
        #         selected_group_indices = ex['SELG']
        #         selected_card_indices = ex['SELCC']
        #         for i in range(len(selected_player_indices)):
        #             events.append(ExSelectEvent(player_turn, selected_player_indices[i], selected_group_indices[i],
        #                                         selected_card_indices[i]))

        elif event_type == 'mustDiscard':
            player_index = ex['PUI']
            group_index = ex['ACTG']
            
            events.append(ExMustDiscard(
                player_turn,
                player_index,
                group_index,
            ))
            
            # Remember who must discard
            must_discard = [player_index, group_index]

        elif event_type == 'noMoreDiscards':
            events.append(ExNoDiscards(
                player_turn,
            ))

        elif event_type == 'hasTrait':
            events.append(ExMustTrait(
                player_turn,
                player_index=ex['PUI'],
            ))

        elif event_type == 'noMoreTraits':
            events.append(ExNoTraits(
                player_turn,
            ))

        elif event_type == 'respawn':
            events.append(ExRespawn(
                player_turn,
                player_indices=ex['TARP'],
                group_indices=ex['TARG'],
                actor_indices=ex['TARA'],
                squares=[list(s) for s in zip(ex['TARXS'], ex['TARYS'])],
                facings=[list(s) for s in zip(ex['TARFXS'], ex['TARFYS'])],
            ))

        elif event_type in ('triggerFail', 'triggerSucceed') and 'TCLOC' in ex:
            location = ex['TCLOC']
            
            if location == 0:
                events.append(ExTriggerInHand(
                    player_turn,
                    die_roll=ex['TROLL'],
                    required_roll=ex['TTHRESH'],
                    hard_to_block=ex['TPEN'],
                    easy_to_block=ex['TBON'],
                    player_index=ex['PUI'],
                    group_index=ex['ACTG'],
                    card_index=ex['ACTC'],
                ))

            elif location == 1:
                events.append(ExTriggerTrait(
                    player_turn,
                    die_roll=ex['TROLL'],
                    required_roll=ex['TTHRESH'],
                    hard_to_block=ex['TPEN'],
                    easy_to_block=ex['TBON'],
                    player_index=ex['PUI'],
                    group_index=ex['ACTG'],
                ))

            elif location == 2:
                events.append(ExTriggerTerrain(
                    player_turn,
                    die_roll=ex['TROLL'],
                    required_roll=ex['TTHRESH'],
                    hard_to_block=ex['TPEN'],
                    easy_to_block=ex['TBON'],
                    square=[ex['TARX'], ex['TARY']],
                ))

        elif event_type == 'target':
            events.append(ExSelectTarget(
                player_turn,
                target_player_indices=ex['TARP'],
                target_group_indices=ex['TARG'],
            ))

        elif event_type == 'selectSquare':
            events.append(ExSelectSquare(
                player_turn,
                square=[ex['TARX'], ex['TARY']],
                facing=[ex['TARFX'], ex['TARFY']],
            ))

        elif event_type == 'genRand':
            events.append(ExRNG(
                player_turn,
                rands=ex['RAND'],
            ))

        elif event_type == 'pass':
            events.append(ExPass(
                player_turn,
            ))

        elif event_type == 'forceLoss':
            events.append(ExResign(
                player_turn,
            ))

        else:
            print('Ignored:', ex)

    return events


# Extract message events
# TODO: Active Player = No Traits
def message_events(battle, messages):
    events = []

    players = battle.players
    groups = [g for p in players for g in p.groups]
    actors = [a for g in groups for a in g.actors]
    player_name = '({})'.format('|'.join(re.escape(p.name) for p in players))
    group_name = '({})'.format('|'.join(re.escape(g.name) for g in groups))
    actor_name = '({})'.format('|'.join(re.escape(a.name) for a in actors))

    start_round = re.compile(r'Starting round (\d+)')
    end_round = re.compile(r'Turn Complete')
    scoring_phase = re.compile(r'Scoring Phase: initiated')
    discard_phase = re.compile(r'Discard Phase: initiated')
    defeat = re.compile(r'{} was defeated'.format(player_name))
    draw = re.compile(r'{} drew (.+) for {}'.format(player_name, group_name))
    reshuffle = re.compile(r"Re-shuffling (\d+) cards from {}'s discard into deck\.".format(group_name))
    failed_draw = re.compile(r"Can not draw for {}\. Deck is empty even after discard reshuffle\.".format(group_name))
    must_trait = re.compile(r'{} must play a Trait'.format(player_name))
    must_target = re.compile(r'Participant {} must select targets'.format(player_name))
    attach_trait = re.compile(r'Attaching (.+) to {}'.format(actor_name))
    detach_trait = re.compile(r'Detaching and discarding (.+) from {}'.format(actor_name))
    attach_terrain = re.compile(r'Attaching (.+) to \((\d+), (\d+)\)')
    active_player = re.compile(r'The active player is now {}'.format(player_name))
    passed = re.compile(r'{} passed\.'.format(player_name))
    ended_round = re.compile(r'{} ended the round.'.format(player_name))
    cancelling = re.compile(r'Action: (.+) is invalid - cancelling')
    cancelled = re.compile(r'(.+) was cancelled\.')
    damage = re.compile(r'{} took (\d+) damage'.format(actor_name))
    heal = re.compile(r'{} healed (\d+)'.format(actor_name))
    die = re.compile(r'{} died'.format(actor_name))
    block = re.compile(r'{}, health = (\d+) \(pi:(\d+), gi:(\d+), ai:(\d+)\)  blocks (.+)'.format(actor_name))
    autoselect = re.compile(r'SeeverSelectCardsCommand:: selected card (.+)')

    for m in messages:
        event = m.get('Event')
        msg = m.get('Msg')

        if event is not None:
            if event == 'StartGame':
                events.append(MsgStartGame())

            elif event == 'GameOver':
                events.append(MsgEndGame())

            elif event == 'Attachment Phase Initiated':
                events.append(MsgTraitPhase())

            elif event == 'Draw Phase Initiated':
                events.append(MsgDrawPhase())

            elif event == 'Action Phase Initiated':
                events.append(MsgActionPhase())

            elif event == 'PlayAction':
                target_names = m['Targets']
                if target_names == '':
                    target_names = []
                elif isinstance(target_names, str):
                    target_names = [target_names]
                
                events.append(MsgCardPlay(
                    actor_name=m['Instigator'],
                    card_name=m['Action'],
                    target_names=target_names,
                ))

            elif event == 'Move':
                events.append(MsgMove(
                    player_name=m['Player'],
                    actor_name=m['Actor'],
                    start=m['Origin'],
                    end=m['Destination'],
                    start_facing=m['StartFacing'],
                    end_facing=m['EndFacing'],
                ))

            elif event.startswith('Trigger'):
                loc = m['TriggerLocation']
                if loc == 'SquareAttachment':
                    msg = MsgTriggerTerrain
                elif loc == 'ActorAttachment':
                    msg = MsgTriggerTrait
                else:
                    msg = MsgTriggerInHand
                    
                events.append(msg(
                    actor_name=m['TriggeringActor'],
                    card_name=m['Trigger'],
                    target=m['AffectedActors'],  # TODO: This might fail when there are multiple targets?
                    success=event.endswith('Succeed'),
                    cause=m['TriggerType'],
                ))

            elif event == 'Needs to discard a card':
                events.append(MsgMustDiscard(
                    group_name=m['Group'],
                ))

            elif event == 'Discard':
                events.append(MsgDiscard(
                    group_name=m['Group'],
                    card_name=m['Card'],
                ))

            elif event == 'SelectCardRequired':
                player_id = m['PlayerID']
                choice_type = m['ChoiceType']  # TODO: What can this be?
                
                events.append(MsgMustSelect(
                    player_name=m['Participant'],
                    option_names=m['Selections'],
                ))

            elif event == 'SelectCard':
                events.append(MsgSelect(
                    player_name=m['Participant'],
                    card_name=m['Selection'],
                ))

            elif event == 'AttachmentExpired':
                loc = m['AttachedTo']
                if isinstance(loc, list):
                    msg = MsgDetachTerrain
                else:
                    msg = MsgDetachTrait
                    
                events.append(msg(
                    loc,
                    card_name=m['Attachment'],
                ))

            elif event == 'startTimer':
                events.append(MsgStartTimer(
                    player_index=m['PlayerIndex'],
                    remaining=m['Remaining'],
                ))

            elif event == 'stopTimer':
                events.append(MsgPauseTimer(
                    player_index=m['PlayerIndex'],
                    remaining=m['Remaining'],
                ))

            else:
                print('Ignored:', m)

        elif msg is not None:
            if start_round.fullmatch(msg):
                match = start_round.fullmatch(msg).groups()
                events.append(MsgStartRound(
                    game_round=int(match[0]),
                ))

            elif end_round.fullmatch(msg):
                events.append(MsgEndRound())

            elif scoring_phase.fullmatch(msg):
                events.append(MsgScoringPhase())

            elif discard_phase.fullmatch(msg):
                events.append(MsgDiscardPhase())

            elif defeat.fullmatch(msg):
                match = defeat.fullmatch(msg).groups()
                events.append(MsgDefeat(
                    player_name=match[0],
                ))

            elif draw.fullmatch(msg):
                match = draw.fullmatch(msg).groups()
                
                if match[1] == 'a card':
                    events.append(MsgHiddenDraw(
                        player_name=match[0],
                        group_name=match[2],
                    ))
                    
                else:
                    events.append(MsgCardDraw(
                        player_name=match[0],
                        group_name=match[2],
                        card_name=match[1],
                    ))

            elif reshuffle.fullmatch(msg):
                match = reshuffle.fullmatch(msg).groups()
                events.append(MsgReshuffle(
                    group_name=match[1],
                    num_cards=int(match[0]),
                ))

            elif failed_draw.fullmatch(msg):
                match = failed_draw.fullmatch(msg).groups()
                events.append(MsgFailedDraw(
                    group_name=match[0],
                ))

            elif must_trait.fullmatch(msg):
                match = must_trait.fullmatch(msg).groups()
                events.append(MsgMustTrait(
                    player_name=match[0],
                ))

            elif must_target.fullmatch(msg):
                match = must_target.fullmatch(msg).groups()
                events.append(MsgMustTarget(
                    player_name=match[0],
                ))

            elif attach_trait.fullmatch(msg):
                match = attach_trait.fullmatch(msg).groups()
                events.append(MsgAttachTrait(
                    actor_name=match[1],
                    card_name=match[0],
                ))

            elif detach_trait.fullmatch(msg):
                match = detach_trait.fullmatch(msg).groups()
                events.append(MsgDetachTrait(
                    actor_name=match[1],
                    card_name=match[0],
                ))

            elif attach_terrain.fullmatch(msg):
                match = attach_terrain.fullmatch(msg).groups()
                events.append(MsgAttachTerrain(
                    square=[int(match[1]), int(match[2])],
                    card_name=match[0],
                ))

            elif active_player.fullmatch(msg):
                match = active_player.fullmatch(msg).groups()
                events.append(MsgPlayerTurn(
                    player_name=match[0],
                ))

            elif passed.fullmatch(msg):
                match = passed.fullmatch(msg).groups()
                events.append(MsgPass(
                    player_name=match[0],
                ))

            elif ended_round.fullmatch(msg):
                match = ended_round.fullmatch(msg).groups()
                events.append(MsgPass(
                    player_name=match[0],
                ))

            elif cancelling.fullmatch(msg):
                match = cancelling.fullmatch(msg).groups()
                events.append(MsgCancelAction(
                    card_name=match[0],
                ))

            elif cancelled.fullmatch(msg):
                match = cancelled.fullmatch(msg).groups()
                events.append(MsgStopCard(
                    card_name=match[0],
                ))

            elif damage.fullmatch(msg):
                match = damage.fullmatch(msg).groups()
                events.append(MsgDamage(
                    actor_name=match[0],
                    hp=int(match[1]),
                ))

            elif heal.fullmatch(msg):
                match = heal.fullmatch(msg).groups()
                events.append(MsgHeal(
                    actor_name=match[0],
                    hp=int(match[1]),
                ))

            elif die.fullmatch(msg):
                match = die.fullmatch(msg).groups()
                events.append(MsgDeath(
                    actor_name=match[0],
                ))

            elif block.fullmatch(msg):
                match = block.fullmatch(msg).groups()
                player_index = int(match[2])
                group_index = int(match[3])
                actor_index = int(match[4])
                
                events.append(MsgBlock(
                    player_index,
                    group_index,
                    actor_index,
                    card_name=match[5],
                ))
                
                events.append(MsgHealth(
                    player_index,
                    group_index,
                    actor_index,
                    hp=int(match[1]),
                ))

            elif autoselect.fullmatch(msg):
                match = autoselect.fullmatch(msg).groups()
                events.append(MsgAutoselect(
                    card_name=match[0],
                ))

            else:
                print('Ignored:', m)

        else:
            print('Ignored:', m)

    return events


# Form higher-level events
def refine_events(battle, ex_events, msg_events):
    # TODO

    for event in ex_events:
        pass
        print(event)

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
        print('Failed to find joinbattle')
        return None, None

    # Parse battle logs
    extensions, messages = log_parse.parse_battle('\n'.join(log_lines[first_line_index:]))
    joinbattle, extensions = extensions[0], extensions[1:]

    # Load objects into battle
    battle = load_battle_objects(joinbattle['objects'])

    if not battle.is_described():
        pass  # Battle not completely started

    # Extract extension events
    ex_events = extension_events(battle, extensions)

    # Extract message events
    msg_events = message_events(battle, messages)

    # Interpolate and extrapolate to form higher-level events
    events = refine_events(battle, ex_events, msg_events)

    return events, battle
