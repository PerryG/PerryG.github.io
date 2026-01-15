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
    player_takes_magic_item
)

app = Flask(__name__, static_folder='.', static_url_path='')

# Current game state (in-memory for now)
current_game: GameState = None


def card_to_dict(card: Card) -> dict:
    """Convert a Card to a JSON-serializable dict."""
    return {
        'name': card.name,
        'cardType': card.card_type.value
    }


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


def game_state_to_dict(game: GameState) -> dict:
    """Convert GameState to a JSON-serializable dict."""
    return {
        'phase': game.phase.value if game.phase else None,
        'players': [player_to_dict(p) for p in game.players],
        'draftState': draft_state_to_dict(game.draft_state),
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


if __name__ == '__main__':
    print("Starting Res Arcana server at http://localhost:5001")
    app.run(debug=True, port=5001)
