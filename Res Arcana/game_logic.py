"""Game logic for Res Arcana setup, drafting, and gameplay."""

import random
from typing import List, Optional, Dict

from game_state import (
    Card, CardType, ControlledCard, DraftState, GamePhase,
    GameState, PlayerState, ResourceType, IncomePhaseState, ActionPhaseState
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

    # Remove card and add to drafted
    draft.cards_to_pick[player_id].remove(card)
    draft.drafted_cards[player_id].append(card)

    # Store remaining cards for passing, clear cards_to_pick
    # (so player doesn't see them until passed back)
    draft.cards_to_pass[player_id] = draft.cards_to_pick[player_id]
    draft.cards_to_pick[player_id] = []

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

    # Redistribute cards_to_pass
    for i in range(num_players):
        if clockwise:
            source = (i - 1) % num_players  # Receive from previous player
        else:
            source = (i + 1) % num_players  # Receive from next player
        draft.cards_to_pick[i] = draft.cards_to_pass.get(source, [])

    # Clear cards_to_pass
    draft.cards_to_pass = {}


def is_draft_round_complete(game: GameState) -> bool:
    """Check if current draft round is complete (all cards drafted)."""
    draft = game.draft_state
    # Round complete when no one has cards left to pass
    return all(len(draft.cards_to_pass.get(i, [])) == 0 for i in range(len(game.players)))


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


# ============================================================
# Income Phase
# ============================================================

def start_income_phase(game: GameState) -> None:
    """Begin the income phase: untap all cards, flip first player token, init state."""
    # Untap all cards for all players
    for player in game.players:
        for cc in player.all_controlled_cards():
            cc.tapped = False

    # Flip first player token face up
    first = game.first_player()
    if first:
        first.first_player_token_face_up = True

    # Initialize income state
    game.income_state = IncomePhaseState()
    for player in game.players:
        pid = player.player_id
        game.income_state.finalized[pid] = False
        game.income_state.waiting_for_earlier[pid] = False
        game.income_state.collection_choices[pid] = {}
        game.income_state.income_choices[pid] = {}
        game.income_state.auto_skip_places_of_power[pid] = True  # Default: skip PoP

    game.phase = GamePhase.INCOME


def get_cards_with_stored_resources(player: PlayerState) -> List[ControlledCard]:
    """Get all controlled cards that have resources stored on them."""
    cards_with_resources = []
    for cc in player.all_controlled_cards():
        if cc.card.name and any(count > 0 for count in cc.resources.values()):
            cards_with_resources.append(cc)
    return cards_with_resources


def get_cards_with_income(player: PlayerState) -> List[ControlledCard]:
    """Get all controlled cards that have income effects."""
    cards_with_income = []
    for cc in player.all_controlled_cards():
        if cc.card.name and cc.card.effects and cc.card.effects.income:
            cards_with_income.append(cc)
    return cards_with_income


def get_cards_needing_income_choice(player: PlayerState) -> List[ControlledCard]:
    """Get cards that require a player choice for income (multiple types to choose from)."""
    cards_needing_choice = []
    for cc in player.all_controlled_cards():
        if cc.card.name and cc.card.effects and cc.card.effects.income:
            income = cc.card.effects.income
            # Need choice if there are multiple types to choose from
            if len(income.types) > 1:
                cards_needing_choice.append(cc)
    return cards_needing_choice


def set_collection_choice(game: GameState, player_id: int, card_name: str, take_all: bool) -> bool:
    """Set whether player will take all resources from a card.

    Returns True if successful.
    """
    if game.phase != GamePhase.INCOME:
        return False

    income_state = game.income_state
    if income_state.finalized[player_id]:
        return False  # Already finalized

    # Verify card exists and has resources
    player = game.get_player(player_id)
    for cc in player.all_controlled_cards():
        if cc.card.name == card_name:
            income_state.collection_choices[player_id][card_name] = take_all
            return True

    return False


def set_income_choice(game: GameState, player_id: int, card_name: str,
                      resources: Dict[str, int]) -> bool:
    """Set the income choice for a card with multiple type options.

    resources is a dict like {'black': 1} or {'red': 1, 'blue': 1}
    Returns True if successful.
    """
    if game.phase != GamePhase.INCOME:
        return False

    income_state = game.income_state
    if income_state.finalized[player_id]:
        return False

    # Verify card exists and has income effect requiring choice
    player = game.get_player(player_id)
    for cc in player.all_controlled_cards():
        if cc.card.name == card_name:
            if cc.card.effects and cc.card.effects.income:
                income = cc.card.effects.income
                # Validate: all chosen types are allowed
                if not all(t in income.types for t in resources.keys()):
                    return False
                # Validate: total count matches
                total = sum(resources.values())
                if total != income.count:
                    return False
                income_state.income_choices[player_id][card_name] = resources
                return True
    return False


def set_auto_skip_places_of_power(game: GameState, player_id: int, auto_skip: bool) -> bool:
    """Set the player's preference for auto-skipping Places of Power resource collection."""
    if game.phase != GamePhase.INCOME:
        return False

    game.income_state.auto_skip_places_of_power[player_id] = auto_skip
    return True


def player_waits_for_earlier(game: GameState, player_id: int) -> bool:
    """Player chooses to wait for all earlier players in turn order to finalize.

    Returns True if successful. First player cannot wait.
    """
    if game.phase != GamePhase.INCOME:
        return False

    income_state = game.income_state
    if income_state.finalized[player_id]:
        return False

    # First player cannot wait
    player = game.get_player(player_id)
    if player.has_first_player_token:
        return False

    income_state.waiting_for_earlier[player_id] = True
    return True


def get_turn_order(game: GameState) -> List[int]:
    """Get player IDs in turn order (starting from first player, clockwise)."""
    first_player_id = None
    for player in game.players:
        if player.has_first_player_token:
            first_player_id = player.player_id
            break

    num_players = len(game.players)
    return [(first_player_id + i) % num_players for i in range(num_players)]


def can_player_finalize(game: GameState, player_id: int) -> bool:
    """Check if player can finalize (not blocked by waiting for earlier players)."""
    if game.phase != GamePhase.INCOME:
        return False

    income_state = game.income_state
    if income_state.finalized[player_id]:
        return False

    # If not waiting, can always finalize
    if not income_state.waiting_for_earlier[player_id]:
        return True

    # If waiting, check all earlier players have finalized
    turn_order = get_turn_order(game)
    for pid in turn_order:
        if pid == player_id:
            break  # Reached self, all earlier players are done
        if not income_state.finalized[pid]:
            return False  # Earlier player not finalized yet

    return True


def player_finalizes_income(game: GameState, player_id: int) -> bool:
    """Player finalizes their income choices.

    Returns True if successful.
    """
    if not can_player_finalize(game, player_id):
        return False

    game.income_state.finalized[player_id] = True

    # Check if all players are done
    if all_income_finalized(game):
        apply_income_and_advance(game)

    return True


def all_income_finalized(game: GameState) -> bool:
    """Check if all players have finalized their income choices."""
    if game.phase != GamePhase.INCOME or not game.income_state:
        return False

    return all(game.income_state.finalized[p.player_id] for p in game.players)


def apply_income_and_advance(game: GameState) -> None:
    """Apply all income choices and move to the action phase."""
    income_state = game.income_state

    for player in game.players:
        pid = player.player_id

        # Apply resource collection choices
        for cc in player.all_controlled_cards():
            card_name = cc.card.name
            if not card_name:
                continue

            # Check if player chose to take resources from this card
            take_all = income_state.collection_choices[pid].get(card_name, False)

            # Auto-skip Places of Power if preference is set
            if cc.card.card_type == CardType.PLACE_OF_POWER:
                if income_state.auto_skip_places_of_power[pid]:
                    take_all = False

            if take_all:
                # Move all resources from card to player
                for res_type, count in list(cc.resources.items()):
                    if count > 0:
                        player.add_resource(res_type, count)
                        cc.resources[res_type] = 0

        # Apply income generation
        for cc in player.all_controlled_cards():
            card_name = cc.card.name
            if not card_name or not cc.card.effects or not cc.card.effects.income:
                continue

            income = cc.card.effects.income

            if len(income.types) == 1:
                # Fixed income: gain count of the single type
                res_type = ResourceType(income.types[0])
                player.add_resource(res_type, income.count)
            else:
                # Multiple types: use player's choice (default to first type if not set)
                chosen = income_state.income_choices[pid].get(card_name)
                if chosen:
                    for res_str, count in chosen.items():
                        res_type = ResourceType(res_str)
                        player.add_resource(res_type, count)
                else:
                    # Default to first type
                    res_type = ResourceType(income.types[0])
                    player.add_resource(res_type, income.count)

    # Clear income state and advance to action phase
    game.income_state = None
    start_action_phase(game)


# ============================================================
# Action Phase
# ============================================================

def start_action_phase(game: GameState) -> None:
    """Begin the action phase: first player starts, track passes."""
    first_player = game.first_player()
    first_player_id = first_player.player_id if first_player else 0

    game.action_state = ActionPhaseState(
        current_player=first_player_id,
        passed={p.player_id: False for p in game.players}
    )
    game.phase = GamePhase.PLAYING


def get_current_player(game: GameState) -> Optional[int]:
    """Get the player ID whose turn it is, or None if round is over."""
    if game.phase != GamePhase.PLAYING or not game.action_state:
        return None
    return game.action_state.current_player


def advance_to_next_player(game: GameState) -> None:
    """Move to the next player who hasn't passed."""
    if not game.action_state:
        return

    num_players = len(game.players)
    current = game.action_state.current_player

    # Find next player who hasn't passed
    for i in range(1, num_players + 1):
        next_player = (current + i) % num_players
        if not game.action_state.passed.get(next_player, False):
            game.action_state.current_player = next_player
            return

    # All players have passed - round ends
    end_action_phase(game)


def all_players_passed(game: GameState) -> bool:
    """Check if all players have passed."""
    if not game.action_state:
        return False
    return all(game.action_state.passed.get(p.player_id, False) for p in game.players)


def end_action_phase(game: GameState) -> None:
    """End the action phase and start the next round's income phase."""
    game.action_state = None
    # Start next round with income phase
    start_income_phase(game)


def player_pass(game: GameState, player_id: int) -> bool:
    """Player passes for the rest of this round.

    If the first player token is face-up, the passing player takes it
    and flips it face-down.
    """
    if game.phase != GamePhase.PLAYING or not game.action_state:
        return False

    if game.action_state.current_player != player_id:
        return False  # Not their turn

    if game.action_state.passed.get(player_id, False):
        return False  # Already passed

    # Handle first player token
    for player in game.players:
        if player.has_first_player_token and player.first_player_token_face_up:
            # Transfer token to passing player and flip face-down
            player.has_first_player_token = False
            passing_player = game.get_player(player_id)
            passing_player.has_first_player_token = True
            passing_player.first_player_token_face_up = False
            break

    # Mark as passed
    game.action_state.passed[player_id] = True

    # Move to next player
    advance_to_next_player(game)
    return True


def can_afford_cost(player: PlayerState, cost: Dict[str, int]) -> bool:
    """Check if player can afford a cost with their current resources."""
    if not cost:
        return True

    # Copy player resources to simulate spending
    available = {rt: player.resource_count(rt) for rt in ResourceType}

    # First, pay specific resource costs
    for resource_str, amount in cost.items():
        if resource_str == 'any':
            continue  # Handle 'any' last
        if resource_str == 'gold':
            rt = ResourceType.GOLD
        else:
            rt = ResourceType(resource_str)
        if available.get(rt, 0) < amount:
            return False
        available[rt] -= amount

    # Then check if we can pay 'any' costs with remaining non-gold resources
    any_cost = cost.get('any', 0)
    if any_cost > 0:
        non_gold_total = sum(
            available.get(rt, 0) for rt in ResourceType if rt != ResourceType.GOLD
        )
        if non_gold_total < any_cost:
            return False

    return True


def pay_cost(player: PlayerState, cost: Dict[str, int], any_payment: Dict[str, int] = None) -> bool:
    """Pay a cost from player's resources.

    any_payment specifies how to pay the 'any' portion (e.g., {'red': 2, 'blue': 1}).
    Returns False if insufficient resources.
    """
    if not cost:
        return True

    if not can_afford_cost(player, cost):
        return False

    # Pay specific costs
    for resource_str, amount in cost.items():
        if resource_str == 'any':
            continue
        if resource_str == 'gold':
            rt = ResourceType.GOLD
        else:
            rt = ResourceType(resource_str)
        player.remove_resource(rt, amount)

    # Pay 'any' costs
    any_cost = cost.get('any', 0)
    if any_cost > 0:
        if any_payment:
            # Use specified payment
            total_paid = 0
            for resource_str, amount in any_payment.items():
                rt = ResourceType(resource_str)
                if rt == ResourceType.GOLD:
                    continue  # 'any' means non-gold
                player.remove_resource(rt, amount)
                total_paid += amount
            if total_paid != any_cost:
                return False  # Didn't pay the right amount
        else:
            # Auto-pay with available non-gold resources
            remaining = any_cost
            for rt in [ResourceType.RED, ResourceType.BLUE, ResourceType.GREEN, ResourceType.BLACK]:
                available = player.resource_count(rt)
                to_pay = min(available, remaining)
                if to_pay > 0:
                    player.remove_resource(rt, to_pay)
                    remaining -= to_pay
                if remaining == 0:
                    break

    return True


def player_play_card(game: GameState, player_id: int, card_name: str,
                     any_payment: Dict[str, int] = None) -> bool:
    """Player plays a card from their hand.

    Returns False if not their turn, card not in hand, or can't afford.
    """
    if game.phase != GamePhase.PLAYING or not game.action_state:
        return False

    if game.action_state.current_player != player_id:
        return False

    player = game.get_player(player_id)

    # Find card in hand
    card = next((c for c in player.hand if c.name == card_name), None)
    if not card:
        return False

    # Check and pay cost
    cost = card.effects.cost if card.effects else None
    if cost and not can_afford_cost(player, cost):
        return False

    if cost:
        pay_cost(player, cost, any_payment)

    # Move card from hand to play
    player.hand.remove(card)
    player.artifacts.append(ControlledCard(card))

    # Move to next player
    advance_to_next_player(game)
    return True


def player_buy_place_of_power(game: GameState, player_id: int, pop_name: str) -> bool:
    """Player buys a Place of Power from the center.

    Returns False if not their turn, PoP not available, or can't afford.
    """
    if game.phase != GamePhase.PLAYING or not game.action_state:
        return False

    if game.action_state.current_player != player_id:
        return False

    player = game.get_player(player_id)

    # Find Place of Power
    pop = next((p for p in game.available_places_of_power if p.name == pop_name), None)
    if not pop:
        return False

    # Check and pay cost
    cost = pop.effects.cost if pop.effects else None
    if cost and not can_afford_cost(player, cost):
        return False

    if cost:
        pay_cost(player, cost)

    # Move PoP to player's control
    game.available_places_of_power.remove(pop)
    player.places_of_power.append(ControlledCard(pop))

    # Move to next player
    advance_to_next_player(game)
    return True


def player_buy_monument(game: GameState, player_id: int, monument_name: str = None,
                        from_deck: bool = False) -> bool:
    """Player buys a Monument.

    monument_name: Name of face-up monument to buy (ignored if from_deck=True)
    from_deck: If True, buy top card of monument deck instead

    All monuments cost 4 gold.
    Returns False if not their turn, monument not available, or can't afford.
    """
    if game.phase != GamePhase.PLAYING or not game.action_state:
        return False

    if game.action_state.current_player != player_id:
        return False

    player = game.get_player(player_id)

    # Monument cost is always 4 gold
    monument_cost = {'gold': 4}
    if not can_afford_cost(player, monument_cost):
        return False

    if from_deck:
        # Buy from top of deck
        if not game.monument_deck:
            return False
        monument = game.monument_deck.pop(0)
    else:
        # Buy face-up monument
        monument = next((m for m in game.available_monuments if m.name == monument_name), None)
        if not monument:
            return False
        game.available_monuments.remove(monument)

        # Replace with top of deck if available
        if game.monument_deck:
            game.available_monuments.append(game.monument_deck.pop(0))

    # Pay cost
    pay_cost(player, monument_cost)

    # Add monument to player
    player.monuments.append(ControlledCard(monument))

    # Move to next player
    advance_to_next_player(game)
    return True


def player_discard_card(game: GameState, player_id: int, card_name: str,
                        gain_gold: bool = False, gain_resources: Dict[str, int] = None) -> bool:
    """Player discards a card from hand to gain resources.

    gain_gold: If True, gain 1 gold
    gain_resources: If provided, gain these resources (must total 2, non-gold only)
                   e.g., {'red': 2} or {'red': 1, 'blue': 1}

    Exactly one of gain_gold or gain_resources must be specified.
    Returns False if not their turn, card not in hand, or invalid resource choice.
    """
    if game.phase != GamePhase.PLAYING or not game.action_state:
        return False

    if game.action_state.current_player != player_id:
        return False

    # Validate exactly one option is chosen
    if gain_gold and gain_resources:
        return False
    if not gain_gold and not gain_resources:
        return False

    player = game.get_player(player_id)

    # Find card in hand
    card = next((c for c in player.hand if c.name == card_name), None)
    if not card:
        return False

    # Validate gain_resources if specified
    if gain_resources:
        total = sum(gain_resources.values())
        if total != 2:
            return False
        # Must be non-gold resources
        for res_type in gain_resources.keys():
            if res_type == 'gold':
                return False
            if res_type not in ['red', 'blue', 'green', 'black']:
                return False

    # Discard the card
    player.hand.remove(card)
    player.discard.append(card)

    # Grant resources
    if gain_gold:
        player.add_resource(ResourceType.GOLD, 1)
    else:
        for res_str, count in gain_resources.items():
            res_type = ResourceType(res_str)
            player.add_resource(res_type, count)

    # Move to next player
    advance_to_next_player(game)
    return True


# ============================================================
# Attack System
# ============================================================

def calculate_attack_payment(player: PlayerState, green_cost: int) -> Dict[str, int]:
    """Calculate what a player must pay for an attack.

    Returns a dict of resources that would be paid.
    - Pay as much green as possible
    - For each missing green, pay 2 other resources
    - If not enough total, pay everything
    """
    available_green = player.resource_count(ResourceType.GREEN)
    green_to_pay = min(available_green, green_cost)
    missing_green = green_cost - green_to_pay

    payment = {'green': green_to_pay}

    # Calculate penalty for missing green (2 resources per missing green)
    penalty_needed = missing_green * 2

    # Collect non-green resources available
    other_available = {}
    for rt in [ResourceType.RED, ResourceType.BLUE, ResourceType.BLACK, ResourceType.GOLD]:
        count = player.resource_count(rt)
        if count > 0:
            other_available[rt.value] = count

    # Pay from other resources
    penalty_paid = 0
    for res_type, count in other_available.items():
        to_pay = min(count, penalty_needed - penalty_paid)
        if to_pay > 0:
            payment[res_type] = to_pay
            penalty_paid += to_pay
        if penalty_paid >= penalty_needed:
            break

    return payment


def get_total_resources(player: PlayerState) -> int:
    """Get total resources a player has."""
    total = 0
    for rt in ResourceType:
        total += player.resource_count(rt)
    return total


def apply_attack_payment(player: PlayerState, payment: Dict[str, int]) -> None:
    """Apply the calculated attack payment, removing resources from player."""
    for res_str, count in payment.items():
        if count > 0:
            rt = ResourceType(res_str)
            player.remove_resource(rt, count)


def can_pay_avoid_cost(player: PlayerState, avoid_cost: Dict) -> bool:
    """Check if player can pay the avoid cost for an attack.

    avoid_cost can be:
    - Resource dict like {'black': 1}
    - {'discard': True} - must have cards in hand
    - {'destroy_artifact': True} - must have artifacts
    """
    if avoid_cost is None:
        return False

    if 'discard' in avoid_cost:
        return len(player.hand) > 0

    if 'destroy_artifact' in avoid_cost:
        return len(player.artifacts) > 0

    # Resource cost
    for res_str, count in avoid_cost.items():
        if res_str in ['red', 'blue', 'green', 'black', 'gold']:
            rt = ResourceType(res_str)
            if player.resource_count(rt) < count:
                return False

    return True


def pay_avoid_cost(player: PlayerState, avoid_cost: Dict,
                   discard_card_name: str = None,
                   destroy_artifact_name: str = None) -> bool:
    """Pay the avoid cost for an attack.

    Returns True if successful.
    """
    if avoid_cost is None:
        return False

    if 'discard' in avoid_cost:
        if discard_card_name:
            card = next((c for c in player.hand if c.name == discard_card_name), None)
            if card:
                player.hand.remove(card)
                player.discard.append(card)
                return True
        return False

    if 'destroy_artifact' in avoid_cost:
        if destroy_artifact_name:
            from game_state import ControlledCard
            artifact = next((a for a in player.artifacts if a.card.name == destroy_artifact_name), None)
            if artifact:
                player.artifacts.remove(artifact)
                player.discard.append(artifact.card)
                return True
        return False

    # Resource cost
    for res_str, count in avoid_cost.items():
        if res_str in ['red', 'blue', 'green', 'black', 'gold']:
            rt = ResourceType(res_str)
            if not player.remove_resource(rt, count):
                return False

    return True


def get_attack_reactions(player: PlayerState, attacker_tags: set = None) -> list:
    """Get available reaction abilities for defending against an attack.

    Returns list of (controlled_card, ability) tuples.
    """
    reactions = []

    for cc in player.all_controlled_cards():
        if cc.tapped:
            continue  # Tapped cards can't use abilities

        if not cc.card.effects or not cc.card.effects.abilities:
            continue

        for ability in cc.card.effects.abilities:
            if ability.trigger != 'attacked':
                continue

            # Check trigger filter (e.g., only react to dragon attacks)
            if ability.trigger_filter:
                if attacker_tags is None or ability.trigger_filter not in attacker_tags:
                    continue

            # Check if any effect is ignore_attack
            has_ignore = any(e.effect_type == 'ignore_attack' for e in ability.effects)
            if has_ignore:
                reactions.append((cc, ability))

    return reactions
