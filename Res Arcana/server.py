"""Flask server for Res Arcana game."""

from flask import Flask, jsonify, request, send_from_directory
import threading
import time
import random

from game_state import GameState, GamePhase, Card, CardType
from game_logic import (
    create_new_game, deal_initial_cards, player_picks_card,
    all_players_have_picked, pass_cards, is_draft_round_complete,
    start_draft_round_2, start_mage_selection, player_selects_mage,
    all_mages_selected, reveal_mages_and_start_magic_items,
    player_takes_magic_item,
    # Income phase
    start_income_phase, set_collection_choice, set_income_choice,
    set_auto_skip_places_of_power, player_waits_for_earlier,
    player_finalizes_income,
    get_cards_with_stored_resources, get_cards_with_income,
    get_cards_needing_income_choice,
    # Action phase
    get_current_player, player_pass, player_play_card,
    player_buy_place_of_power, player_buy_monument, player_discard_card,
    can_afford_cost,
    # Abilities
    get_activatable_abilities, use_ability, get_passive_cost_reduction,
    # Victory
    calculate_player_points, calculate_player_resources_value
)

app = Flask(__name__, static_folder='.', static_url_path='')

# Current game state (in-memory for now)
current_game: GameState = None

# Bot thread management
bot_threads = []
bot_stop_event = threading.Event()
game_lock = threading.Lock()


def stop_all_bots():
    """Stop all running bot threads."""
    global bot_threads
    bot_stop_event.set()
    for t in bot_threads:
        t.join(timeout=2)
    bot_threads = []
    bot_stop_event.clear()


def start_bots(human_player_id: int, num_players: int):
    """Start bot threads for all non-human players."""
    stop_all_bots()

    for player_id in range(num_players):
        if player_id != human_player_id:
            t = threading.Thread(target=run_bot, args=(player_id,), daemon=True)
            t.start()
            bot_threads.append(t)
            print(f"Started bot for player {player_id}", flush=True)


def run_bot(player_id: int):
    """Bot main loop - runs in background thread."""
    while not bot_stop_event.is_set():
        try:
            with game_lock:
                if current_game is not None:
                    bot_take_action(player_id)
        except Exception as e:
            print(f"Bot {player_id} error: {e}")

        time.sleep(0.5)


def bot_take_action(player_id: int):
    """Take an action for the bot based on current game phase."""
    game = current_game
    if game is None:
        return

    phase = game.phase

    if phase in (GamePhase.DRAFTING_ROUND_1, GamePhase.DRAFTING_ROUND_2):
        bot_handle_draft(game, player_id)
    elif phase == GamePhase.MAGE_SELECTION:
        bot_handle_mage_selection(game, player_id)
    elif phase == GamePhase.MAGIC_ITEM_SELECTION:
        bot_handle_magic_item_selection(game, player_id)
    elif phase == GamePhase.INCOME:
        bot_handle_income(game, player_id)
    elif phase == GamePhase.PLAYING:
        bot_handle_action(game, player_id)


def bot_handle_draft(game: GameState, player_id: int):
    """Bot picks a random card during drafting."""
    draft = game.draft_state
    if not draft:
        return

    cards = draft.cards_to_pick.get(player_id, [])
    if not cards:
        return

    card = random.choice(cards)
    print(f"Bot {player_id} picking: {card.name}", flush=True)

    if player_picks_card(game, player_id, card):
        # Check for phase advancement
        if all_players_have_picked(game):
            if is_draft_round_complete(game):
                if game.phase == GamePhase.DRAFTING_ROUND_1:
                    start_draft_round_2(game)
                else:
                    start_mage_selection(game)
            else:
                pass_cards(game)


def bot_handle_mage_selection(game: GameState, player_id: int):
    """Bot picks a random mage."""
    draft = game.draft_state
    if not draft:
        return

    if draft.selected_mage.get(player_id) is not None:
        return  # Already selected

    mages = draft.mage_options.get(player_id, [])
    if not mages:
        return

    mage = random.choice(mages)
    print(f"Bot {player_id} selecting mage: {mage.name}", flush=True)

    if player_selects_mage(game, player_id, mage):
        if all_mages_selected(game):
            reveal_mages_and_start_magic_items(game)


def bot_handle_magic_item_selection(game: GameState, player_id: int):
    """Bot picks a magic item when it's their turn."""
    draft = game.draft_state
    if not draft:
        return

    if draft.magic_item_selector != player_id:
        return  # Not our turn

    items = game.available_magic_items
    if not items:
        return

    item = random.choice(items)
    print(f"Bot {player_id} taking magic item: {item.name}", flush=True)
    player_takes_magic_item(game, player_id, item)


def bot_handle_income(game: GameState, player_id: int):
    """Bot handles income phase - makes choices and finalizes."""
    income = game.income_state
    if not income:
        return

    if income.finalized.get(player_id, False):
        return  # Already finalized

    player = game.get_player(player_id)

    # Make income choices for cards that need them
    for cc in get_cards_needing_income_choice(player):
        card_name = cc.card.name
        if card_name not in income.income_choices.get(player_id, {}):
            inc = cc.card.effects.income
            # Random distribution among allowed types
            resources = {}
            for _ in range(inc.count):
                t = random.choice(inc.types)
                resources[t] = resources.get(t, 0) + 1
            print(f"Bot {player_id} choosing income for {card_name}: {resources}", flush=True)
            set_income_choice(game, player_id, card_name, resources)
            return  # One action per tick

    # Make collection choices
    for cc in get_cards_with_stored_resources(player):
        card_name = cc.card.name
        if card_name not in income.collection_choices.get(player_id, {}):
            take = random.choice([True, False])
            print(f"Bot {player_id} {'taking' if take else 'leaving'} resources from {card_name}", flush=True)
            set_collection_choice(game, player_id, card_name, take)
            return

    # Finalize
    print(f"Bot {player_id} finalizing income", flush=True)
    player_finalizes_income(game, player_id)


def bot_handle_action(game: GameState, player_id: int):
    """Bot handles action phase - takes actions when it's their turn."""
    action = game.action_state
    if not action:
        return

    # Not our turn?
    if action.current_player != player_id:
        return

    # Already passed?
    if action.passed.get(player_id, False):
        return

    player = game.get_player(player_id)

    # Gather possible actions
    possible_actions = []

    # Check for usable abilities
    abilities = get_activatable_abilities(game, player_id)
    if abilities:
        possible_actions.append(('use_ability', abilities))

    # Check for playable cards in hand
    playable_cards = []
    for card in player.hand:
        cost = card.effects.cost if card.effects else None
        if cost is None or can_afford_cost(player, cost):
            playable_cards.append(card)
    if playable_cards:
        possible_actions.append(('play_card', playable_cards))

    # Check for affordable Places of Power
    affordable_pops = []
    for pop in game.available_places_of_power:
        cost = pop.effects.cost if pop.effects else None
        if cost is None or can_afford_cost(player, cost):
            affordable_pops.append(pop)
    if affordable_pops:
        possible_actions.append(('buy_pop', affordable_pops))

    # Check for monument purchase (4 gold)
    monument_cost = {'gold': 4}
    if can_afford_cost(player, monument_cost):
        # Can buy from face-up or deck
        monument_options = []
        for mon in game.available_monuments:
            monument_options.append(('face_up', mon))
        if game.monument_deck:
            monument_options.append(('deck', None))
        if monument_options:
            possible_actions.append(('buy_monument', monument_options))

    # Check for discard option (if we have cards in hand)
    if player.hand:
        possible_actions.append(('discard', player.hand))

    # If no possible actions, must pass
    if not possible_actions:
        print(f"Bot {player_id} passing (no actions available)", flush=True)
        # Pick a random magic item from the center
        if game.available_magic_items:
            new_item = random.choice(game.available_magic_items)
            player_pass(game, player_id, new_item.name)
        else:
            player_pass(game, player_id)
        return

    # Random chance to pass even if actions available (to end rounds eventually)
    if random.random() < 0.3:
        print(f"Bot {player_id} passing (choosing to pass)", flush=True)
        # Pick a random magic item from the center
        if game.available_magic_items:
            new_item = random.choice(game.available_magic_items)
            player_pass(game, player_id, new_item.name)
        else:
            player_pass(game, player_id)
        return

    # Pick a random action type
    action_type, options = random.choice(possible_actions)

    if action_type == 'use_ability':
        ability_info = random.choice(options)
        card_name = ability_info['card_name']
        ability_index = ability_info['ability_index']
        print(f"Bot {player_id} using ability on {card_name} (index {ability_index})", flush=True)
        # Simple ability use without complex choices
        use_ability(game, player_id, card_name, ability_index)

    elif action_type == 'play_card':
        card = random.choice(options)
        print(f"Bot {player_id} playing card: {card.name}", flush=True)
        player_play_card(game, player_id, card.name)

    elif action_type == 'buy_pop':
        pop = random.choice(options)
        print(f"Bot {player_id} buying Place of Power: {pop.name}", flush=True)
        player_buy_place_of_power(game, player_id, pop.name)

    elif action_type == 'buy_monument':
        choice = random.choice(options)
        if choice[0] == 'deck':
            print(f"Bot {player_id} buying monument from deck", flush=True)
            player_buy_monument(game, player_id, from_deck=True)
        else:
            mon = choice[1]
            print(f"Bot {player_id} buying monument: {mon.name}", flush=True)
            player_buy_monument(game, player_id, mon.name)

    elif action_type == 'discard':
        card = random.choice(options)
        # Randomly choose gold or 2 non-gold
        if random.random() < 0.5:
            print(f"Bot {player_id} discarding {card.name} for 1 gold", flush=True)
            player_discard_card(game, player_id, card.name, gain_gold=True)
        else:
            # Random 2 non-gold resources
            resource_types = ['red', 'blue', 'green', 'black']
            r1 = random.choice(resource_types)
            r2 = random.choice(resource_types)
            if r1 == r2:
                gain = {r1: 2}
            else:
                gain = {r1: 1, r2: 1}
            print(f"Bot {player_id} discarding {card.name} for {gain}", flush=True)
            player_discard_card(game, player_id, card.name, gain_resources=gain)


def ability_cost_to_dict(cost) -> dict:
    """Convert an AbilityCost to a JSON-serializable dict."""
    result = {'costType': cost.cost_type}
    if cost.resources:
        result['resources'] = cost.resources
    if cost.tag:
        result['tag'] = cost.tag
    if cost.cost_type == 'destroy_artifact':
        result['mustBeDifferent'] = cost.must_be_different
    if cost.cost_type == 'pay_variable':
        result['minAmount'] = cost.min_amount
        result['sameType'] = cost.same_type
        if cost.types:
            result['types'] = cost.types
    return result


def ability_effect_to_dict(effect) -> dict:
    """Convert an AbilityEffect to a JSON-serializable dict."""
    result = {'effectType': effect.effect_type}
    if effect.resources:
        result['resources'] = effect.resources
    if effect.count is not None:
        result['count'] = effect.count
    if effect.types:
        result['types'] = effect.types
    if effect.green_cost is not None:
        result['greenCost'] = effect.green_cost
    if effect.avoid_cost is not None:
        result['avoidCost'] = effect.avoid_cost
    if effect.target:
        result['target'] = effect.target
    if effect.source:
        result['source'] = effect.source
    if effect.discount is not None:
        result['discount'] = effect.discount
    if effect.free:
        result['free'] = effect.free
    if effect.card_filter:
        result['cardFilter'] = effect.card_filter
    if effect.check_resource:
        result['checkResource'] = effect.check_resource
    if effect.check_tag:
        result['checkTag'] = effect.check_tag
    if effect.bonus:
        result['bonus'] = effect.bonus
    if effect.amount_from_paid:
        result['amountFromPaid'] = effect.amount_from_paid
    if effect.different_from_paid:
        result['differentFromPaid'] = effect.different_from_paid
    return result


def ability_to_dict(ability) -> dict:
    """Convert an Ability to a JSON-serializable dict."""
    result = {
        'costs': [ability_cost_to_dict(c) for c in ability.costs],
        'effects': [ability_effect_to_dict(e) for e in ability.effects]
    }
    if ability.trigger:
        result['trigger'] = ability.trigger
    if ability.trigger_filter:
        result['triggerFilter'] = ability.trigger_filter
    return result


def passive_to_dict(passive) -> dict:
    """Convert a PassiveEffect to a JSON-serializable dict."""
    result = {'effectType': passive.effect_type}
    if passive.card_filter:
        result['cardFilter'] = passive.card_filter
    if passive.amount:
        result['amount'] = passive.amount
    if passive.reduction_type:
        result['reductionType'] = passive.reduction_type
    return result


def card_to_dict(card: Card) -> dict:
    """Convert a Card to a JSON-serializable dict."""
    result = {
        'name': card.name,
        'cardType': card.card_type.value
    }

    # Include tags if present
    if card.tags:
        result['tags'] = list(card.tags)

    # Include points if non-zero
    if card.points:
        result['points'] = card.points

    # Include effects if present
    if card.effects:
        effects = {}
        if card.effects.income:
            income = card.effects.income
            effects['income'] = {
                'count': income.count,
                'types': income.types,
                'conditional': income.conditional,
                'addToCard': income.add_to_card
            }
        if card.effects.cost:
            effects['cost'] = card.effects.cost
        if card.effects.abilities:
            effects['abilities'] = [ability_to_dict(a) for a in card.effects.abilities]
        if card.effects.passives:
            effects['passives'] = [passive_to_dict(p) for p in card.effects.passives]
        if effects:
            result['effects'] = effects

    return result


def controlled_card_to_dict(cc) -> dict:
    """Convert a ControlledCard to a JSON-serializable dict."""
    return {
        'card': card_to_dict(cc.card),
        'tapped': cc.tapped,
        'resources': {k.value: v for k, v in cc.resources.items()}
    }


def player_to_dict(player, viewing_player_id: int = None) -> dict:
    """Convert a PlayerState to a JSON-serializable dict.

    If viewing_player_id is provided and differs from this player,
    hand and deck contents are hidden (only counts shown).
    """
    is_self = viewing_player_id is None or player.player_id == viewing_player_id

    result = {
        'playerId': player.player_id,
        'mage': controlled_card_to_dict(player.mage),
        'magicItem': controlled_card_to_dict(player.magic_item),
        'artifacts': [controlled_card_to_dict(a) for a in player.artifacts],
        'monuments': [controlled_card_to_dict(m) for m in player.monuments],
        'placesOfPower': [controlled_card_to_dict(p) for p in player.places_of_power],
        'scrolls': [card_to_dict(s) for s in player.scrolls],
        'discard': [card_to_dict(c) for c in player.discard],
        'resources': {k.value: v for k, v in player.resources.items()},
        'hasFirstPlayerToken': player.has_first_player_token,
        'firstPlayerTokenFaceUp': player.first_player_token_face_up,
        # Victory point info
        'points': calculate_player_points(player),
        'resourceValue': calculate_player_resources_value(player)
    }

    # Hand and deck: show contents only to owning player
    if is_self:
        result['hand'] = [card_to_dict(c) for c in player.hand]
        result['deck'] = [card_to_dict(c) for c in player.deck]
    else:
        result['hand'] = []  # Hidden
        result['deck'] = []  # Hidden

    # Always include counts for UI
    result['handCount'] = len(player.hand)
    result['deckCount'] = len(player.deck)

    return result


def draft_state_to_dict(draft_state, viewing_player_id: int = None) -> dict:
    """Convert DraftState to a JSON-serializable dict.

    If viewing_player_id is provided, hides other players' draft info:
    - Other players' cards_to_pick (only show count)
    - Other players' mage_options (only show count)
    - Other players' selected_mage before reveal (show as 'hidden')
    """
    if draft_state is None:
        return None

    result = {
        'cardsToPick': {},
        'draftedCards': {},
        'mageOptions': {},
        'selectedMage': {},
        'magicItemSelector': draft_state.magic_item_selector
    }

    for player_id, cards in draft_state.cards_to_pick.items():
        is_self = viewing_player_id is None or player_id == viewing_player_id
        if is_self:
            result['cardsToPick'][str(player_id)] = [card_to_dict(c) for c in cards]
        else:
            # Hide contents, just show count
            result['cardsToPick'][str(player_id)] = []

    for player_id, cards in draft_state.drafted_cards.items():
        is_self = viewing_player_id is None or player_id == viewing_player_id
        if is_self:
            result['draftedCards'][str(player_id)] = [card_to_dict(c) for c in cards]
        else:
            # Other players' drafted cards are hidden until game starts
            result['draftedCards'][str(player_id)] = []

    for player_id, mages in draft_state.mage_options.items():
        is_self = viewing_player_id is None or player_id == viewing_player_id
        if is_self:
            result['mageOptions'][str(player_id)] = [card_to_dict(c) for c in mages]
        else:
            # Other players' mage options are hidden
            result['mageOptions'][str(player_id)] = []

    for player_id, mage in draft_state.selected_mage.items():
        is_self = viewing_player_id is None or player_id == viewing_player_id
        if is_self:
            result['selectedMage'][str(player_id)] = card_to_dict(mage) if mage else None
        else:
            # Show that they've selected (True) or not (None), but not which mage
            result['selectedMage'][str(player_id)] = 'hidden' if mage else None

    return result


def income_state_to_dict(income_state, game: GameState) -> dict:
    """Convert IncomePhaseState to a JSON-serializable dict."""
    if income_state is None:
        return None

    # Build info about cards needing choices for each player
    cards_info = {}
    for player in game.players:
        pid = player.player_id
        # Cards with resources that can be collected
        cards_with_resources = []
        for cc in get_cards_with_stored_resources(player):
            cards_with_resources.append({
                'cardName': cc.card.name,
                'cardType': cc.card.card_type.value,
                'resources': {k.value: v for k, v in cc.resources.items() if v > 0}
            })

        # Cards with income that need choices (multiple types)
        cards_needing_choice = []
        for cc in get_cards_needing_income_choice(player):
            income = cc.card.effects.income
            cards_needing_choice.append({
                'cardName': cc.card.name,
                'cardType': cc.card.card_type.value,
                'count': income.count,
                'types': income.types
            })

        # Cards with fixed income (single type, no choice needed)
        cards_with_fixed_income = []
        for cc in get_cards_with_income(player):
            income = cc.card.effects.income
            if len(income.types) == 1:
                cards_with_fixed_income.append({
                    'cardName': cc.card.name,
                    'cardType': cc.card.card_type.value,
                    'count': income.count,
                    'type': income.types[0]
                })

        cards_info[str(pid)] = {
            'cardsWithResources': cards_with_resources,
            'cardsNeedingChoice': cards_needing_choice,
            'cardsWithFixedIncome': cards_with_fixed_income
        }

    return {
        'finalized': {str(k): v for k, v in income_state.finalized.items()},
        'waitingForEarlier': {str(k): v for k, v in income_state.waiting_for_earlier.items()},
        'collectionChoices': {str(k): v for k, v in income_state.collection_choices.items()},
        'incomeChoices': {str(k): v for k, v in income_state.income_choices.items()},
        'autoSkipPlacesOfPower': {str(k): v for k, v in income_state.auto_skip_places_of_power.items()},
        'cardsInfo': cards_info
    }


def action_state_to_dict(action_state, game: GameState) -> dict:
    """Convert ActionPhaseState to a JSON-serializable dict."""
    if action_state is None:
        return None

    return {
        'currentPlayer': action_state.current_player,
        'passed': {str(k): v for k, v in action_state.passed.items()}
    }


def game_state_to_dict(game: GameState, viewing_player_id: int = None) -> dict:
    """Convert GameState to a JSON-serializable dict.

    If viewing_player_id is provided, hides information that player shouldn't see:
    - Other players' hands and decks
    - Other players' mage options and draft cards
    """
    result = {
        'phase': game.phase.value if game.phase else None,
        'players': [player_to_dict(p, viewing_player_id) for p in game.players],
        'draftState': draft_state_to_dict(game.draft_state, viewing_player_id),
        'incomeState': income_state_to_dict(game.income_state, game),
        'actionState': action_state_to_dict(game.action_state, game),
        'availableMonuments': [card_to_dict(c) for c in game.available_monuments],
        'availablePlacesOfPower': [card_to_dict(c) for c in game.available_places_of_power],
        'availableMagicItems': [card_to_dict(c) for c in game.available_magic_items],
        'availableScrolls': [card_to_dict(c) for c in game.available_scrolls],
        'monumentDeck': [{} for _ in game.monument_deck],  # Hidden contents
        'monumentDeckCount': len(game.monument_deck)
    }

    # Include victory result if game is over
    if game.victory_result:
        result['victoryResult'] = game.victory_result

    return result


# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)


# API endpoints
@app.route('/api/new-game', methods=['POST'])
def new_game():
    """Create a new game.

    Body: {numPlayers: 2-4, humanPlayerId: 0 (default)}
    Bots are automatically started for all non-human players.
    """
    global current_game

    data = request.get_json() or {}
    num_players = data.get('numPlayers', 2)
    human_player_id = data.get('humanPlayerId', 0)

    if num_players < 2 or num_players > 4:
        return jsonify({'error': 'Game supports 2-4 players'}), 400

    if human_player_id < 0 or human_player_id >= num_players:
        return jsonify({'error': 'Invalid humanPlayerId'}), 400

    with game_lock:
        current_game = create_new_game(num_players)
        deal_initial_cards(current_game)

    # Start bots for non-human players
    start_bots(human_player_id, num_players)

    return jsonify(game_state_to_dict(current_game, human_player_id))


@app.route('/api/state')
def get_state():
    """Get current game state filtered for a specific player.

    Query params:
        playerId: Player ID to filter visible information (recommended).
                  If omitted, returns state filtered for player 0.
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    player_id_str = request.args.get('playerId')
    viewing_player_id = int(player_id_str) if player_id_str is not None else 0

    with game_lock:
        return jsonify(game_state_to_dict(current_game, viewing_player_id))


# Set to False in production to disable debug endpoint
DEBUG_MODE = True


@app.route('/api/state/full')
def get_full_state():
    """Get full game state without filtering (debug only).

    This endpoint exposes all hidden information and should be
    disabled in production by setting DEBUG_MODE = False.
    """
    global current_game

    if not DEBUG_MODE:
        return jsonify({'error': 'Debug endpoint disabled'}), 403

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    return jsonify(game_state_to_dict(current_game, viewing_player_id=None))


@app.route('/api/draft/pick', methods=['POST'])
def draft_pick():
    """Pick a card during drafting."""
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    card_name = data.get('cardName')

    with game_lock:
        # Find the card in player's available cards
        draft_state = current_game.draft_state
        cards_to_pick = draft_state.cards_to_pick.get(player_id, [])

        card = next((c for c in cards_to_pick if c.name == card_name), None)
        if card is None:
            return jsonify({'error': 'Card not found'}), 400

        if not player_picks_card(current_game, player_id, card):
            return jsonify({'error': 'Cannot pick that card'}), 400

        # Check if we should advance (all players picked via their own clients/bots)
        if all_players_have_picked(current_game):
            if is_draft_round_complete(current_game):
                if current_game.phase == GamePhase.DRAFTING_ROUND_1:
                    start_draft_round_2(current_game)
                else:
                    start_mage_selection(current_game)
            else:
                pass_cards(current_game)

        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/mage/select', methods=['POST'])
def mage_select():
    """Select a mage."""
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    mage_name = data.get('mageName')

    with game_lock:
        # Find the mage in player's options
        draft_state = current_game.draft_state
        mage_options = draft_state.mage_options.get(player_id, [])

        mage = next((m for m in mage_options if m.name == mage_name), None)
        if mage is None:
            return jsonify({'error': 'Mage not found'}), 400

        if not player_selects_mage(current_game, player_id, mage):
            return jsonify({'error': 'Cannot select that mage'}), 400

        # Check if all mages selected (each player selects via their own client/bot)
        if all_mages_selected(current_game):
            reveal_mages_and_start_magic_items(current_game)

        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/magic-item/select', methods=['POST'])
def magic_item_select():
    """Select a magic item."""
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    item_name = data.get('itemName')

    with game_lock:
        # Find the magic item
        item = next((i for i in current_game.available_magic_items if i.name == item_name), None)
        if item is None:
            return jsonify({'error': 'Magic item not found'}), 400

        if not player_takes_magic_item(current_game, player_id, item):
            return jsonify({'error': 'Cannot take that magic item'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


# Income phase endpoints

@app.route('/api/income/start', methods=['POST'])
def income_start():
    """Start the income phase (typically called at start of each round)."""
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json() or {}
    player_id = data.get('playerId', 0)

    with game_lock:
        if current_game.phase != GamePhase.PLAYING:
            return jsonify({'error': 'Can only start income from playing phase'}), 400

        start_income_phase(current_game)
        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/income/collection-choice', methods=['POST'])
def income_collection_choice():
    """Set whether to collect resources from a card.

    Body: {playerId, cardName, takeAll: bool}
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    card_name = data.get('cardName')
    take_all = data.get('takeAll', False)

    with game_lock:
        if not set_collection_choice(current_game, player_id, card_name, take_all):
            return jsonify({'error': 'Cannot set collection choice'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/income/income-choice', methods=['POST'])
def income_income_choice():
    """Set income choice for a card with options.

    Body: {playerId, cardName, resources: {red: 1, ...}}
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    card_name = data.get('cardName')
    resources = data.get('resources', {})

    with game_lock:
        if not set_income_choice(current_game, player_id, card_name, resources):
            return jsonify({'error': 'Cannot set income choice'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/income/toggle-auto-skip-pop', methods=['POST'])
def income_toggle_auto_skip():
    """Toggle auto-skip Places of Power preference.

    Body: {playerId, autoSkip: bool}
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    auto_skip = data.get('autoSkip', True)

    with game_lock:
        if not set_auto_skip_places_of_power(current_game, player_id, auto_skip):
            return jsonify({'error': 'Cannot set preference'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/income/wait', methods=['POST'])
def income_wait():
    """Player waits for earlier players to finalize.

    Body: {playerId}
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')

    with game_lock:
        if not player_waits_for_earlier(current_game, player_id):
            return jsonify({'error': 'Cannot wait (maybe first player or already finalized)'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/income/finalize', methods=['POST'])
def income_finalize():
    """Finalize income choices.

    Body: {playerId}
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')

    with game_lock:
        if not player_finalizes_income(current_game, player_id):
            return jsonify({'error': 'Cannot finalize (maybe waiting for earlier players)'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


# Action phase endpoints

@app.route('/api/action/pass', methods=['POST'])
def action_pass():
    """Player passes for the rest of the round.

    Body: {playerId, newMagicItem?: string}
    When passing, player must swap their magic item with one from the center.
    If newMagicItem not specified, takes the first available item.
    If first player token is face-up, passing player takes it (face-down).
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    new_magic_item = data.get('newMagicItem')

    with game_lock:
        if not player_pass(current_game, player_id, new_magic_item):
            return jsonify({'error': 'Cannot pass (not your turn, already passed, or invalid magic item)'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/action/play-card', methods=['POST'])
def action_play_card():
    """Play a card from hand.

    Body: {playerId, cardName, anyPayment?: {red: 1, ...}}
    anyPayment specifies how to pay 'any' cost portion.
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    card_name = data.get('cardName')
    any_payment = data.get('anyPayment')

    with game_lock:
        if not player_play_card(current_game, player_id, card_name, any_payment):
            return jsonify({'error': 'Cannot play card (not your turn, not in hand, or cannot afford)'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/action/buy-place-of-power', methods=['POST'])
def action_buy_pop():
    """Buy a Place of Power.

    Body: {playerId, popName}
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    pop_name = data.get('popName')

    with game_lock:
        if not player_buy_place_of_power(current_game, player_id, pop_name):
            return jsonify({'error': 'Cannot buy Place of Power (not your turn, not available, or cannot afford)'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/action/buy-monument', methods=['POST'])
def action_buy_monument():
    """Buy a Monument.

    Body: {playerId, monumentName?, fromDeck?: bool}
    monumentName: name of face-up monument (ignored if fromDeck=true)
    fromDeck: buy top of monument deck instead of face-up
    All monuments cost 4 gold.
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    monument_name = data.get('monumentName')
    from_deck = data.get('fromDeck', False)

    with game_lock:
        if not player_buy_monument(current_game, player_id, monument_name, from_deck):
            return jsonify({'error': 'Cannot buy monument (not your turn, not available, or cannot afford)'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


@app.route('/api/action/discard-card', methods=['POST'])
def action_discard_card():
    """Discard a card from hand to gain resources.

    Body: {playerId, cardName, gainGold?: bool, gainResources?: {red: 1, blue: 1}}
    gainGold: if true, gain 1 gold
    gainResources: gain 2 total non-gold resources (e.g., {red: 2} or {red: 1, green: 1})
    Exactly one of gainGold or gainResources must be specified.
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    card_name = data.get('cardName')
    gain_gold = data.get('gainGold', False)
    gain_resources = data.get('gainResources')

    with game_lock:
        if not player_discard_card(current_game, player_id, card_name, gain_gold, gain_resources):
            return jsonify({'error': 'Cannot discard card (not your turn, card not in hand, or invalid resource choice)'}), 400

        return jsonify(game_state_to_dict(current_game, player_id))


# Ability endpoints

@app.route('/api/action/get-abilities', methods=['GET'])
def action_get_abilities():
    """Get all abilities the player can currently activate.

    Query params: playerId
    Returns list of {cardName, abilityIndex, costs, effects}
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    player_id = int(request.args.get('playerId', 0))

    with game_lock:
        abilities = get_activatable_abilities(current_game, player_id)
        # Convert costs and effects to dicts
        result = []
        for ab in abilities:
            result.append({
                'cardName': ab['card_name'],
                'abilityIndex': ab['ability_index'],
                'costs': [ability_cost_to_dict(c) for c in ab['costs']],
                'effects': [ability_effect_to_dict(e) for e in ab['effects']]
            })
        return jsonify({'abilities': result})


@app.route('/api/action/use-ability', methods=['POST'])
def action_use_ability():
    """Use an ability on a card.

    Body: {
        playerId,
        cardName,
        abilityIndex,
        costChoices?: {
            tap_card?: string,        // card name to tap
            destroy_artifact?: string, // artifact name to destroy
            discard?: string,         // card name to discard
            any_payment?: {red: 1, ...} // how to pay 'any' costs
        },
        effectChoices?: {
            resource_choices?: {red: 1, blue: 1}, // for choice effects
            untap_target?: string,    // card name for untap effects
            add_to_card_target?: string, // target for add_to_card
            take_from_card_target?: string, // target for take_from_card
            play_card?: string,       // card name for play_card effects
            attack_responses?: {      // for attacks
                [playerId]: 'pay' | 'avoid' | 'reaction',
                [playerId + '_avoid']?: {discard?: string, destroy_artifact?: string}
            }
        }
    }
    """
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    card_name = data.get('cardName')
    ability_index = data.get('abilityIndex', 0)
    cost_choices = data.get('costChoices', {})
    effect_choices = data.get('effectChoices', {})

    with game_lock:
        result = use_ability(
            current_game, player_id, card_name, ability_index,
            cost_choices, effect_choices
        )

        if not result.get('success', False):
            return jsonify({'error': result.get('error', 'Failed to use ability')}), 400

        # Return game state along with ability result
        response = game_state_to_dict(current_game, player_id)
        response['abilityResult'] = result
        return jsonify(response)


if __name__ == '__main__':
    print("Starting Res Arcana server at http://localhost:5001")
    # use_reloader=False to prevent bot threads from being killed on code reload
    app.run(debug=True, port=5001, use_reloader=False)
