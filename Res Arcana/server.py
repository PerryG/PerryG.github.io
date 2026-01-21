"""Flask server for Res Arcana game."""

from flask import Flask, jsonify, request, send_from_directory
from dataclasses import asdict
import os

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
    player_finalizes_income, can_player_finalize,
    get_cards_with_stored_resources, get_cards_with_income,
    get_cards_needing_income_choice
)

app = Flask(__name__, static_folder='.', static_url_path='')

# Current game state (in-memory for now)
current_game: GameState = None


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


def player_to_dict(player) -> dict:
    """Convert a PlayerState to a JSON-serializable dict."""
    return {
        'playerId': player.player_id,
        'mage': controlled_card_to_dict(player.mage),
        'magicItem': controlled_card_to_dict(player.magic_item),
        'artifacts': [controlled_card_to_dict(a) for a in player.artifacts],
        'monuments': [controlled_card_to_dict(m) for m in player.monuments],
        'placesOfPower': [controlled_card_to_dict(p) for p in player.places_of_power],
        'scrolls': [card_to_dict(s) for s in player.scrolls],
        'hand': [card_to_dict(c) for c in player.hand],
        'deck': [card_to_dict(c) for c in player.deck],
        'discard': [card_to_dict(c) for c in player.discard],
        'resources': {k.value: v for k, v in player.resources.items()},
        'hasFirstPlayerToken': player.has_first_player_token,
        'firstPlayerTokenFaceUp': player.first_player_token_face_up
    }


def draft_state_to_dict(draft_state) -> dict:
    """Convert DraftState to a JSON-serializable dict."""
    if draft_state is None:
        return None

    return {
        'cardsToPick': {
            str(k): [card_to_dict(c) for c in v]
            for k, v in draft_state.cards_to_pick.items()
        },
        'draftedCards': {
            str(k): [card_to_dict(c) for c in v]
            for k, v in draft_state.drafted_cards.items()
        },
        'mageOptions': {
            str(k): [card_to_dict(c) for c in v]
            for k, v in draft_state.mage_options.items()
        },
        'selectedMage': {
            str(k): card_to_dict(v) if v else None
            for k, v in draft_state.selected_mage.items()
        },
        'magicItemSelector': draft_state.magic_item_selector
    }


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


def game_state_to_dict(game: GameState) -> dict:
    """Convert GameState to a JSON-serializable dict."""
    return {
        'phase': game.phase.value if game.phase else None,
        'players': [player_to_dict(p) for p in game.players],
        'draftState': draft_state_to_dict(game.draft_state),
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
    """Create a new game."""
    global current_game

    data = request.get_json() or {}
    num_players = data.get('numPlayers', 2)

    if num_players < 2 or num_players > 4:
        return jsonify({'error': 'Game supports 2-4 players'}), 400

    current_game = create_new_game(num_players)
    deal_initial_cards(current_game)

    return jsonify(game_state_to_dict(current_game))


@app.route('/api/state')
def get_state():
    """Get current game state."""
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    return jsonify(game_state_to_dict(current_game))


@app.route('/api/draft/pick', methods=['POST'])
def draft_pick():
    """Pick a card during drafting."""
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    card_name = data.get('cardName')

    # Find the card in player's available cards
    draft_state = current_game.draft_state
    cards_to_pick = draft_state.cards_to_pick.get(player_id, [])

    card = next((c for c in cards_to_pick if c.name == card_name), None)
    if card is None:
        return jsonify({'error': 'Card not found'}), 400

    if not player_picks_card(current_game, player_id, card):
        return jsonify({'error': 'Cannot pick that card'}), 400

    # For single-player testing, simulate other players picking
    # (In a real multiplayer game, we'd wait for all players)
    for pid in range(len(current_game.players)):
        if pid != player_id:
            other_cards = draft_state.cards_to_pick.get(pid, [])
            if other_cards:
                player_picks_card(current_game, pid, other_cards[0])

    # Check if we should advance
    if all_players_have_picked(current_game):
        if is_draft_round_complete(current_game):
            if current_game.phase == GamePhase.DRAFTING_ROUND_1:
                start_draft_round_2(current_game)
            else:
                start_mage_selection(current_game)
        else:
            pass_cards(current_game)

    return jsonify(game_state_to_dict(current_game))


@app.route('/api/mage/select', methods=['POST'])
def mage_select():
    """Select a mage."""
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    mage_name = data.get('mageName')

    # Find the mage in player's options
    draft_state = current_game.draft_state
    mage_options = draft_state.mage_options.get(player_id, [])

    mage = next((m for m in mage_options if m.name == mage_name), None)
    if mage is None:
        return jsonify({'error': 'Mage not found'}), 400

    if not player_selects_mage(current_game, player_id, mage):
        return jsonify({'error': 'Cannot select that mage'}), 400

    # For single-player testing, simulate other players selecting
    for pid in range(len(current_game.players)):
        if pid != player_id:
            other_mages = draft_state.mage_options.get(pid, [])
            if other_mages and draft_state.selected_mage.get(pid) is None:
                player_selects_mage(current_game, pid, other_mages[0])

    # Check if all mages selected
    if all_mages_selected(current_game):
        reveal_mages_and_start_magic_items(current_game)

    return jsonify(game_state_to_dict(current_game))


@app.route('/api/magic-item/select', methods=['POST'])
def magic_item_select():
    """Select a magic item."""
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    data = request.get_json()
    player_id = data.get('playerId')
    item_name = data.get('itemName')

    # Find the magic item
    item = next((i for i in current_game.available_magic_items if i.name == item_name), None)
    if item is None:
        return jsonify({'error': 'Magic item not found'}), 400

    if not player_takes_magic_item(current_game, player_id, item):
        return jsonify({'error': 'Cannot take that magic item'}), 400

    # For single-player testing, auto-pick for other players
    # Keep picking until it's the original player's turn again or game moves to PLAYING
    while (current_game.phase == GamePhase.MAGIC_ITEM_SELECTION and
           current_game.draft_state and
           current_game.draft_state.magic_item_selector != player_id and
           current_game.available_magic_items):
        next_selector = current_game.draft_state.magic_item_selector
        # Pick first available item for this player
        next_item = current_game.available_magic_items[0]
        player_takes_magic_item(current_game, next_selector, next_item)

    return jsonify(game_state_to_dict(current_game))


# Income phase endpoints

@app.route('/api/income/start', methods=['POST'])
def income_start():
    """Start the income phase (typically called at start of each round)."""
    global current_game

    if current_game is None:
        return jsonify({'error': 'No game in progress'}), 404

    if current_game.phase != GamePhase.PLAYING:
        return jsonify({'error': 'Can only start income from playing phase'}), 400

    start_income_phase(current_game)
    return jsonify(game_state_to_dict(current_game))


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

    if not set_collection_choice(current_game, player_id, card_name, take_all):
        return jsonify({'error': 'Cannot set collection choice'}), 400

    return jsonify(game_state_to_dict(current_game))


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

    if not set_income_choice(current_game, player_id, card_name, resources):
        return jsonify({'error': 'Cannot set income choice'}), 400

    return jsonify(game_state_to_dict(current_game))


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

    if not set_auto_skip_places_of_power(current_game, player_id, auto_skip):
        return jsonify({'error': 'Cannot set preference'}), 400

    return jsonify(game_state_to_dict(current_game))


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

    if not player_waits_for_earlier(current_game, player_id):
        return jsonify({'error': 'Cannot wait (maybe first player or already finalized)'}), 400

    return jsonify(game_state_to_dict(current_game))


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

    if not player_finalizes_income(current_game, player_id):
        return jsonify({'error': 'Cannot finalize (maybe waiting for earlier players)'}), 400

    # For single-player testing, auto-finalize other players
    for pid in range(len(current_game.players)):
        if pid != player_id and current_game.phase == GamePhase.INCOME:
            if can_player_finalize(current_game, pid):
                player_finalizes_income(current_game, pid)

    return jsonify(game_state_to_dict(current_game))


if __name__ == '__main__':
    print("Starting Res Arcana server at http://localhost:5001")
    app.run(debug=True, port=5001)
