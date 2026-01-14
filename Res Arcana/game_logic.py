"""Game logic for Res Arcana setup and drafting."""

import random
from typing import List, Optional

from game_state import (
    Card, CardType, ControlledCard, DraftState, GamePhase,
    GameState, PlayerState, ResourceType
)
from cards import (
    ARTIFACTS, MAGES, MONUMENTS, MAGIC_ITEMS, SCROLLS,
    PLACES_OF_POWER_PAIRS
)


def select_places_of_power(num_players: int) -> List[Card]:
    """Select places of power respecting double-sided card constraint.

    Returns player_count + 2 places of power.
    """
    count_needed = num_players + 2
    available_pairs = list(PLACES_OF_POWER_PAIRS)
    random.shuffle(available_pairs)

    selected = []
    for pair in available_pairs:
        if len(selected) >= count_needed:
            break
        # Pick a random side of this card
        side = random.choice([0, 1])
        selected.append(pair[side])

    return selected


def select_monuments(num_players: int) -> tuple[List[Card], List[Card]]:
    """Select monuments for the game.

    Returns (available_monuments, monument_deck).
    2 players: 7 total, 3 players: 10 total, 4 players: 12 total.
    2 are face-up/available, rest go in deck.
    """
    counts = {2: 7, 3: 10, 4: 12}
    total = counts.get(num_players, 10)

    all_monuments = list(MONUMENTS)
    random.shuffle(all_monuments)
    selected = all_monuments[:total]

    available = selected[:2]
    deck = selected[2:]
    return available, deck


def create_empty_player(player_id: int) -> PlayerState:
    """Create an empty player state (no mage/magic item yet)."""
    # We need placeholder mage/magic_item since they're required fields
    # These will be replaced during setup
    placeholder_mage = ControlledCard(Card("", CardType.MAGE))
    placeholder_item = ControlledCard(Card("", CardType.MAGIC_ITEM))
    return PlayerState(
        player_id=player_id,
        mage=placeholder_mage,
        magic_item=placeholder_item,
    )


def create_new_game(num_players: int) -> GameState:
    """Initialize a new game in SETUP phase."""
    if num_players < 2 or num_players > 4:
        raise ValueError("Game supports 2-4 players")

    # Create empty players
    players = [create_empty_player(i) for i in range(num_players)]

    # Assign first player token randomly
    first_player = random.randint(0, num_players - 1)
    players[first_player].has_first_player_token = True

    # Set up shared zones
    available_places = select_places_of_power(num_players)
    available_monuments, monument_deck = select_monuments(num_players)

    # All magic items and scrolls are available
    all_magic_items = list(MAGIC_ITEMS)
    all_scrolls = list(SCROLLS)

    game = GameState(
        players=players,
        phase=GamePhase.SETUP,
        available_monuments=available_monuments,
        monument_deck=monument_deck,
        available_places_of_power=available_places,
        available_magic_items=all_magic_items,
        available_scrolls=all_scrolls,
    )

    return game


def deal_initial_cards(game: GameState) -> None:
    """Deal 2 mages and 4 artifacts to each player to start drafting."""
    num_players = len(game.players)

    # Shuffle decks
    all_mages = list(MAGES)
    all_artifacts = list(ARTIFACTS)
    random.shuffle(all_mages)
    random.shuffle(all_artifacts)

    # Initialize draft state
    game.draft_state = DraftState()

    for i, player in enumerate(game.players):
        # Deal 2 mages
        game.draft_state.mage_options[i] = [all_mages.pop(), all_mages.pop()]
        game.draft_state.selected_mage[i] = None

        # Deal 4 artifacts
        artifacts = [all_artifacts.pop() for _ in range(4)]
        game.draft_state.cards_to_pick[i] = artifacts
        game.draft_state.drafted_cards[i] = []

    # Store remaining artifacts for round 2
    game._remaining_artifacts = all_artifacts

    game.phase = GamePhase.DRAFTING_ROUND_1


def player_picks_card(game: GameState, player_id: int, card: Card) -> bool:
    """Player picks a card from their available cards during draft.

    Returns True if successful, False if card not available.
    """
    if game.phase not in (GamePhase.DRAFTING_ROUND_1, GamePhase.DRAFTING_ROUND_2):
        return False

    draft = game.draft_state
    if card not in draft.cards_to_pick[player_id]:
        return False

    # Move card from available to drafted
    draft.cards_to_pick[player_id].remove(card)
    draft.drafted_cards[player_id].append(card)
    return True


def all_players_have_picked(game: GameState) -> bool:
    """Check if all players have picked a card this round."""
    draft = game.draft_state
    # Everyone should have the same number of cards to pick
    # If someone has one fewer drafted card, they haven't picked yet
    if not draft.drafted_cards:
        return False

    drafted_counts = [len(draft.drafted_cards[i]) for i in range(len(game.players))]
    return len(set(drafted_counts)) == 1  # All same count


def pass_cards(game: GameState) -> None:
    """Pass remaining cards to the next player.

    Round 1: clockwise (player i -> player i+1)
    Round 2: counter-clockwise (player i -> player i-1)
    """
    draft = game.draft_state
    num_players = len(game.players)

    # Determine pass direction
    clockwise = game.phase == GamePhase.DRAFTING_ROUND_1

    # Collect all cards to pass
    old_cards = {i: draft.cards_to_pick[i] for i in range(num_players)}

    # Redistribute
    for i in range(num_players):
        if clockwise:
            source = (i - 1) % num_players  # Receive from previous player
        else:
            source = (i + 1) % num_players  # Receive from next player
        draft.cards_to_pick[i] = old_cards[source]


def is_draft_round_complete(game: GameState) -> bool:
    """Check if current draft round is complete (all cards drafted)."""
    draft = game.draft_state
    # Round complete when no one has cards left to pick
    return all(len(draft.cards_to_pick[i]) == 0 for i in range(len(game.players)))


def start_draft_round_2(game: GameState) -> None:
    """Deal 4 more artifacts and start round 2 (counter-clockwise)."""
    remaining = game._remaining_artifacts

    for i in range(len(game.players)):
        artifacts = [remaining.pop() for _ in range(4)]
        game.draft_state.cards_to_pick[i] = artifacts

    game.phase = GamePhase.DRAFTING_ROUND_2


def start_mage_selection(game: GameState) -> None:
    """Transition to mage selection phase after drafting."""
    game.phase = GamePhase.MAGE_SELECTION


def player_selects_mage(game: GameState, player_id: int, mage: Card) -> bool:
    """Player secretly selects one of their two mages.

    Returns True if successful.
    """
    if game.phase != GamePhase.MAGE_SELECTION:
        return False

    draft = game.draft_state
    if mage not in draft.mage_options[player_id]:
        return False

    draft.selected_mage[player_id] = mage
    return True


def all_mages_selected(game: GameState) -> bool:
    """Check if all players have selected a mage."""
    draft = game.draft_state
    return all(draft.selected_mage[i] is not None for i in range(len(game.players)))


def reveal_mages_and_start_magic_items(game: GameState) -> None:
    """Reveal all mages and transition to magic item selection."""
    draft = game.draft_state

    # Assign selected mages to players
    for i, player in enumerate(game.players):
        selected = draft.selected_mage[i]
        player.mage = ControlledCard(selected)

    # Determine magic item selection order (reverse of play order)
    # Play order is based on first player token, going clockwise
    # So we go counter-clockwise from first player
    first_player_id = None
    for player in game.players:
        if player.has_first_player_token:
            first_player_id = player.player_id
            break

    # Last player in turn order picks first
    num_players = len(game.players)
    last_player = (first_player_id - 1) % num_players
    draft.magic_item_selector = last_player

    game.phase = GamePhase.MAGIC_ITEM_SELECTION


def player_takes_magic_item(game: GameState, player_id: int, magic_item: Card) -> bool:
    """Player takes a magic item from the available pool.

    Returns True if successful.
    """
    if game.phase != GamePhase.MAGIC_ITEM_SELECTION:
        return False

    draft = game.draft_state
    if player_id != draft.magic_item_selector:
        return False

    if magic_item not in game.available_magic_items:
        return False

    # Give magic item to player
    player = game.get_player(player_id)
    player.magic_item = ControlledCard(magic_item)
    game.available_magic_items.remove(magic_item)

    # Move to next player (counter-clockwise from current selector)
    num_players = len(game.players)
    next_selector = (draft.magic_item_selector - 1) % num_players

    # Check if all players have magic items
    all_have_items = all(
        p.magic_item.card.name != "" for p in game.players
    )

    if all_have_items:
        setup_starting_hands(game)
    else:
        draft.magic_item_selector = next_selector

    return True


def setup_starting_hands(game: GameState) -> None:
    """Distribute drafted cards: 3 random to hand, 5 to deck."""
    draft = game.draft_state

    for i, player in enumerate(game.players):
        drafted = list(draft.drafted_cards[i])
        random.shuffle(drafted)

        # 3 to hand, 5 to deck
        player.hand = drafted[:3]
        player.deck = drafted[3:]

    # Clear draft state and start game
    game.draft_state = None
    game.phase = GamePhase.PLAYING


# High-level flow helpers

def advance_draft(game: GameState) -> None:
    """Advance the draft state after all players have picked."""
    if not all_players_have_picked(game):
        return

    if is_draft_round_complete(game):
        if game.phase == GamePhase.DRAFTING_ROUND_1:
            start_draft_round_2(game)
        else:
            start_mage_selection(game)
    else:
        pass_cards(game)
