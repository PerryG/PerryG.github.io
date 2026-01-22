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
    get_cards_needing_income_choice
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


def card_to_dict(card: Card) -> dict:
    """Convert a Card to a JSON-serializable dict."""
    result = {
        'name': card.name,
        'cardType': card.card_type.value
    }

    # Include effects if present
    if card.effects:
        effects = {}
        if card.effects.income:
            income = card.effects.income
            effects['income'] = {
                'count': income.count,
                'types': income.types
            }
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
        'firstPlayerTokenFaceUp': player.first_player_token_face_up
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


def game_state_to_dict(game: GameState, viewing_player_id: int = None) -> dict:
    """Convert GameState to a JSON-serializable dict.

    If viewing_player_id is provided, hides information that player shouldn't see:
    - Other players' hands and decks
    - Other players' mage options and draft cards
    """
    return {
        'phase': game.phase.value if game.phase else None,
        'players': [player_to_dict(p, viewing_player_id) for p in game.players],
        'draftState': draft_state_to_dict(game.draft_state, viewing_player_id),
        'incomeState': income_state_to_dict(game.income_state, game),
        'availableMonuments': [card_to_dict(c) for c in game.available_monuments],
        'availablePlacesOfPower': [card_to_dict(c) for c in game.available_places_of_power],
        'availableMagicItems': [card_to_dict(c) for c in game.available_magic_items],
        'availableScrolls': [card_to_dict(c) for c in game.available_scrolls],
        'monumentDeck': [{} for _ in game.monument_deck]  # Hidden contents
    }


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


if __name__ == '__main__':
    print("Starting Res Arcana server at http://localhost:5001")
    # use_reloader=False to prevent bot threads from being killed on code reload
    app.run(debug=True, port=5001, use_reloader=False)
