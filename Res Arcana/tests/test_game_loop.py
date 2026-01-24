#!/usr/bin/env python3
"""Tests for game loop features: victory check, magic item swap, points calculation."""

import sys
sys.path.insert(0, '..')

from game_state import *
from game_logic import *
from cards import ARTIFACTS


def test_points_calculation():
    """Test that player points are calculated correctly."""
    print("=== Test: Points calculation ===")
    game = create_new_game(2)
    game.draft_state = None
    game.phase = GamePhase.PLAYING

    player = game.players[0]
    player.has_first_player_token = True  # +1 point

    # Give player an artifact with points
    bone_dragon = next(c for c in ARTIFACTS if c.name == "Bone Dragon")
    player.artifacts = [ControlledCard(bone_dragon)]  # +1 point

    points = calculate_player_points(player)
    assert points == 2, f"Expected 2 points, got {points}"
    print(f"  Player points: {points} (correct)")


def test_resource_value_calculation():
    """Test resource value calculation for tie-breaking (gold counts as 2)."""
    print("=== Test: Resource value calculation ===")
    game = create_new_game(2)
    player = game.players[0]

    player.resources = {ResourceType.GOLD: 2, ResourceType.RED: 3}
    # Value should be 2*2 + 3 = 7
    value = calculate_player_resources_value(player)
    assert value == 7, f"Expected 7, got {value}"
    print(f"  Resource value: {value} (correct)")


def test_victory_check_no_winner():
    """Test victory check when no one has 10+ points."""
    print("=== Test: Victory check (no winner) ===")
    game = create_new_game(2)
    game.draft_state = None
    game.phase = GamePhase.PLAYING

    result = check_victory(game)
    assert not result['game_over'], "Game should not be over"
    print(f"  Game over: {result['game_over']} (correct)")


def test_victory_check_winner():
    """Test victory check when a player has 10+ points."""
    print("=== Test: Victory check (winner) ===")
    game = create_new_game(2)
    game.draft_state = None
    game.phase = GamePhase.PLAYING

    player = game.players[0]
    player.has_first_player_token = True  # +1 point

    # Give player 9 Bone Dragons = 9 points, + 1 from first player = 10
    bone_dragon = next(c for c in ARTIFACTS if c.name == "Bone Dragon")
    player.artifacts = [ControlledCard(bone_dragon) for _ in range(9)]

    points = calculate_player_points(player)
    assert points == 10, f"Expected 10 points, got {points}"

    result = check_victory(game)
    assert result['game_over'], "Game should be over"
    assert result['winner'] == 0, f"Expected winner 0, got {result['winner']}"
    print(f"  Player points: {points}, Winner: {result['winner']} (correct)")


def test_victory_check_tie():
    """Test victory check when players are tied."""
    print("=== Test: Victory check (tie) ===")
    game = create_new_game(2)
    game.draft_state = None
    game.phase = GamePhase.PLAYING

    bone_dragon = next(c for c in ARTIFACTS if c.name == "Bone Dragon")

    # Clear first player token (it gives +1 point)
    for player in game.players:
        player.has_first_player_token = False

    # Both players have 10 points
    for player in game.players:
        player.artifacts = [ControlledCard(bone_dragon) for _ in range(10)]
        player.resources = {ResourceType.RED: 5}  # Same resources too

    result = check_victory(game)
    assert result['game_over'], "Game should be over"
    assert result['is_tie'], "Should be a tie"
    print(f"  Is tie: {result['is_tie']} (correct)")


def test_victory_check_tie_breaker():
    """Test that resource value breaks ties."""
    print("=== Test: Victory check (tie-breaker) ===")
    game = create_new_game(2)
    game.draft_state = None
    game.phase = GamePhase.PLAYING

    bone_dragon = next(c for c in ARTIFACTS if c.name == "Bone Dragon")

    # Clear first player token (it gives +1 point)
    for player in game.players:
        player.has_first_player_token = False

    # Both players have 10 points
    for player in game.players:
        player.artifacts = [ControlledCard(bone_dragon) for _ in range(10)]

    # Player 1 has more resources (gold counts as 2)
    game.players[0].resources = {ResourceType.RED: 5}  # value = 5
    game.players[1].resources = {ResourceType.GOLD: 3}  # value = 6

    result = check_victory(game)
    assert result['game_over'], "Game should be over"
    assert not result['is_tie'], "Should not be a tie"
    assert result['winner'] == 1, f"Expected winner 1 (more resources), got {result['winner']}"
    print(f"  Winner: {result['winner']} (correct - had more resources)")


def test_magic_item_swap_on_pass():
    """Test that passing swaps magic items correctly."""
    print("=== Test: Magic item swap on pass ===")
    game = create_new_game(2)
    game.draft_state = None
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})

    # Set up player's magic item (use one that's NOT in the available pool)
    # Use item index 1 to ensure it's different from available_magic_items[0]
    from cards import MAGIC_ITEMS
    game.players[0].magic_item = ControlledCard(MAGIC_ITEMS[1])  # "Calm | Elan"
    initial_magic_item = game.players[0].magic_item.card.name
    available_count_before = len(game.available_magic_items)

    # Make sure the initial item is not in the available pool
    game.available_magic_items = [m for m in game.available_magic_items if m.name != initial_magic_item]

    # Player passes with specific magic item choice
    new_item_name = game.available_magic_items[0].name
    result = player_pass(game, 0, new_item_name)

    assert result, "Pass should succeed"

    new_magic_item = game.players[0].magic_item.card.name
    assert new_magic_item == new_item_name, f"Expected {new_item_name}, got {new_magic_item}"

    # Old item should be back in the pool
    available_names = [m.name for m in game.available_magic_items]
    assert initial_magic_item in available_names, "Old item should be returned to pool"
    assert new_item_name not in available_names, "New item should be removed from pool"

    print(f"  Swapped {initial_magic_item} for {new_item_name} (correct)")


def test_first_player_token_transfer_on_pass():
    """Test that first player token transfers correctly when passing."""
    print("=== Test: First player token transfer on pass ===")
    game = create_new_game(2)
    game.draft_state = None
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})

    # Player 1 has the token face-up
    game.players[0].has_first_player_token = False
    game.players[1].has_first_player_token = True
    game.players[1].first_player_token_face_up = True

    # Player 0 passes first
    new_item = game.available_magic_items[0].name
    player_pass(game, 0, new_item)

    # Player 0 should now have the token (face-down)
    assert game.players[0].has_first_player_token, "Passing player should get token"
    assert not game.players[0].first_player_token_face_up, "Token should be face-down"
    assert not game.players[1].has_first_player_token, "Previous holder should not have token"

    print("  First player token transferred correctly")


def test_fixed_income():
    """Test that fixed income gives all specified resources (AND, not OR)."""
    print("=== Test: Fixed income (AND) ===")
    game = create_new_game(2)
    game.draft_state = None
    game.phase = GamePhase.INCOME
    game.income_state = IncomePhaseState()

    player = game.players[0]
    player.player_id = 0
    game.income_state.finalized[0] = False
    game.income_state.finalized[1] = True  # Other player already done
    game.income_state.waiting_for_earlier[0] = False
    game.income_state.waiting_for_earlier[1] = False
    game.income_state.collection_choices[0] = {}
    game.income_state.collection_choices[1] = {}
    game.income_state.income_choices[0] = {}
    game.income_state.income_choices[1] = {}
    game.income_state.auto_skip_places_of_power[0] = True
    game.income_state.auto_skip_places_of_power[1] = True

    # Give player Chalice of Life (income: 1 blue AND 1 green)
    chalice = next(c for c in ARTIFACTS if c.name == "Chalice of Life")
    player.artifacts = [ControlledCard(chalice)]
    player.resources = {}  # Start with nothing

    # Finalize income (triggers apply_income_and_advance)
    player_finalizes_income(game, 0)

    # Player should have BOTH 1 blue AND 1 green
    assert player.resource_count(ResourceType.BLUE) == 1, f"Expected 1 blue, got {player.resource_count(ResourceType.BLUE)}"
    assert player.resource_count(ResourceType.GREEN) == 1, f"Expected 1 green, got {player.resource_count(ResourceType.GREEN)}"
    print(f"  Got 1 blue AND 1 green (correct)")


def test_choice_income():
    """Test that choice income allows player to choose resources."""
    print("=== Test: Choice income (OR) ===")
    game = create_new_game(2)
    game.draft_state = None
    game.phase = GamePhase.INCOME
    game.income_state = IncomePhaseState()

    player = game.players[0]
    player.player_id = 0
    game.income_state.finalized[0] = False
    game.income_state.finalized[1] = True
    game.income_state.waiting_for_earlier[0] = False
    game.income_state.waiting_for_earlier[1] = False
    game.income_state.collection_choices[0] = {}
    game.income_state.collection_choices[1] = {}
    game.income_state.income_choices[1] = {}
    game.income_state.auto_skip_places_of_power[0] = True
    game.income_state.auto_skip_places_of_power[1] = True

    # Give player Celestial Horse (income: 2 from red/blue/green - choice)
    horse = next(c for c in ARTIFACTS if c.name == "Celestial Horse")
    player.artifacts = [ControlledCard(horse)]
    player.resources = {}

    # Player chooses to get 2 red
    game.income_state.income_choices[0] = {"Celestial Horse": {"red": 2}}

    player_finalizes_income(game, 0)

    # Player should have 2 red (their choice)
    assert player.resource_count(ResourceType.RED) == 2, f"Expected 2 red, got {player.resource_count(ResourceType.RED)}"
    assert player.resource_count(ResourceType.BLUE) == 0, "Should have 0 blue"
    assert player.resource_count(ResourceType.GREEN) == 0, "Should have 0 green"
    print(f"  Got 2 red (player's choice - correct)")


def run_all_tests():
    """Run all game loop tests."""
    print("\n" + "="*60)
    print("GAME LOOP TESTS")
    print("="*60 + "\n")

    test_points_calculation()
    test_resource_value_calculation()
    test_victory_check_no_winner()
    test_victory_check_winner()
    test_victory_check_tie()
    test_victory_check_tie_breaker()
    test_magic_item_swap_on_pass()
    test_first_player_token_transfer_on_pass()
    test_fixed_income()
    test_choice_income()

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
