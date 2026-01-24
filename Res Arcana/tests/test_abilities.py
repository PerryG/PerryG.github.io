#!/usr/bin/env python3
"""Tests for card ability system: costs, effects, attacks, etc."""

import sys
sys.path.insert(0, '..')

from game_state import *
from game_logic import *
from cards import ARTIFACTS


def test_tap_ability():
    """Test basic tap ability (Dwarven Pickaxe: tap+red -> gold)."""
    print("=== Test: Tap ability ===")
    game = create_new_game(2)
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})
    game.draft_state = None

    player = game.players[0]
    pickaxe = next(c for c in ARTIFACTS if c.name == "Dwarven Pickaxe")
    player.artifacts = [ControlledCard(pickaxe)]
    player.resources = {ResourceType.RED: 1}

    result = use_ability(game, 0, "Dwarven Pickaxe", 0)

    assert result['success'], f"Ability should succeed: {result}"
    assert player.resource_count(ResourceType.GOLD) == 1, "Should have 1 gold"
    assert player.resource_count(ResourceType.RED) == 0, "Should have spent the red"
    assert player.artifacts[0].tapped, "Card should be tapped"
    print("  Tap ability works correctly")


def test_add_to_card_ability():
    """Test ability that adds resources to card (Athanor)."""
    print("=== Test: Add to card ability ===")
    game = create_new_game(2)
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})
    game.draft_state = None

    player = game.players[0]
    athanor = next(c for c in ARTIFACTS if c.name == "Athanor")
    player.artifacts = [ControlledCard(athanor)]
    player.resources = {ResourceType.RED: 1}

    result = use_ability(game, 0, "Athanor", 0)

    assert result['success'], f"Ability should succeed: {result}"
    assert player.artifacts[0].resource_count(ResourceType.RED) == 2, "Should have 2 red on card"
    print("  Add to card ability works correctly")


def test_attack_ability():
    """Test attack ability (Elvish Bow: tap -> attack 1 green)."""
    print("=== Test: Attack ability ===")
    game = create_new_game(2)
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})
    game.draft_state = None

    player = game.players[0]
    opponent = game.players[1]

    bow = next(c for c in ARTIFACTS if c.name == "Elvish Bow")
    player.artifacts = [ControlledCard(bow)]
    opponent.resources = {ResourceType.GREEN: 2}

    result = use_ability(game, 0, "Elvish Bow", 1)  # Second ability is attack

    assert result['success'], f"Ability should succeed: {result}"
    assert opponent.resource_count(ResourceType.GREEN) == 1, "Opponent should have lost 1 green"
    print("  Attack ability works correctly")


def test_tap_another_card_cost():
    """Test tap another card as cost (Cursed Dwarven King: tap+tap dragon -> gold)."""
    print("=== Test: Tap another card as cost ===")
    game = create_new_game(2)
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})
    game.draft_state = None

    player = game.players[0]

    cdk = next(c for c in ARTIFACTS if c.name == "Cursed Dwarven King")
    fire_dragon = next(c for c in ARTIFACTS if c.name == "Fire Dragon")
    player.artifacts = [ControlledCard(cdk), ControlledCard(fire_dragon)]

    result = use_ability(game, 0, "Cursed Dwarven King", 1,
                        cost_choices={'tap_card': 'Fire Dragon'})

    assert result['success'], f"Ability should succeed: {result}"
    assert player.resource_count(ResourceType.GOLD) == 1, "Should have 1 gold"
    assert player.artifacts[0].tapped, "CDK should be tapped"
    assert player.artifacts[1].tapped, "Fire Dragon should be tapped"
    print("  Tap another card cost works correctly")


def test_destroy_artifact_cost():
    """Test destroy artifact as cost (Fiery Whip: destroy -> gain resources)."""
    print("=== Test: Destroy artifact as cost ===")
    game = create_new_game(2)
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})
    game.draft_state = None

    player = game.players[0]

    fiery_whip = next(c for c in ARTIFACTS if c.name == "Fiery Whip")
    dwarven_pickaxe = next(c for c in ARTIFACTS if c.name == "Dwarven Pickaxe")
    magical_shard = next(c for c in ARTIFACTS if c.name == "Magical Shard")

    player.artifacts = [
        ControlledCard(fiery_whip),
        ControlledCard(dwarven_pickaxe),
        ControlledCard(magical_shard)
    ]

    result = use_ability(game, 0, "Fiery Whip", 1,
                        cost_choices={'destroy_artifact': 'Dwarven Pickaxe'},
                        effect_choices={
                            'destroyed_card_name': 'Dwarven Pickaxe',
                            'destroyed_card_cost': {'red': 1},
                            'bonus_resource': 'black'
                        })

    assert result['success'], f"Ability should succeed: {result}"
    assert len(player.artifacts) == 2, "Should have 2 artifacts left"
    artifact_names = [a.card.name for a in player.artifacts]
    assert 'Dwarven Pickaxe' not in artifact_names, "Pickaxe should be destroyed"
    assert player.resource_count(ResourceType.RED) == 1, "Should have gained 1 red (from cost)"
    assert player.resource_count(ResourceType.BLACK) == 2, "Should have gained 2 black (bonus)"
    print("  Destroy artifact cost works correctly")


def test_resource_choice_effect():
    """Test effect with resource choice (Magical Shard: tap -> 1 non-gold choice)."""
    print("=== Test: Resource choice effect ===")
    game = create_new_game(2)
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})
    game.draft_state = None

    player = game.players[0]

    magical_shard = next(c for c in ARTIFACTS if c.name == "Magical Shard")
    player.artifacts = [ControlledCard(magical_shard)]

    result = use_ability(game, 0, "Magical Shard", 0,
                        effect_choices={'resource_choices': {'blue': 1}})

    assert result['success'], f"Ability should succeed: {result}"
    assert player.resource_count(ResourceType.BLUE) == 1, "Should have 1 blue"
    print("  Resource choice effect works correctly")


def test_passive_cost_reduction():
    """Test passive cost reduction (Dragon Bridle: dragons cost 3 less)."""
    print("=== Test: Passive cost reduction ===")
    game = create_new_game(2)
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})
    game.draft_state = None

    player = game.players[0]

    dragon_bridle = next(c for c in ARTIFACTS if c.name == "Dragon Bridle")
    fire_dragon = next(c for c in ARTIFACTS if c.name == "Fire Dragon")  # Cost: 6 red

    player.artifacts = [ControlledCard(dragon_bridle)]
    player.hand = [fire_dragon]
    player.resources = {ResourceType.RED: 3}  # Only 3 red (normally needs 6)

    result = player_play_card(game, 0, "Fire Dragon")

    assert result, "Should be able to play Fire Dragon with reduced cost"
    assert len(player.artifacts) == 2, "Should have 2 artifacts now"
    assert player.resource_count(ResourceType.RED) == 0, "Should have spent 3 red"
    print("  Passive cost reduction works correctly")


def test_convert_ability():
    """Test convert ability (Athanor: convert non-gold to gold)."""
    print("=== Test: Convert ability ===")
    game = create_new_game(2)
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})
    game.draft_state = None

    player = game.players[0]

    athanor = next(c for c in ARTIFACTS if c.name == "Athanor")
    cc = ControlledCard(athanor)
    cc.resources = {ResourceType.RED: 6}  # Put 6 red on the card
    player.artifacts = [cc]
    player.resources = {ResourceType.RED: 2, ResourceType.BLUE: 3}  # 5 resources in pool

    result = use_ability(game, 0, "Athanor", 1)  # Second ability is convert

    assert result['success'], f"Ability should succeed: {result}"
    # All non-gold in pool should be converted to gold
    assert player.resource_count(ResourceType.GOLD) == 5, "Should have 5 gold"
    assert player.resource_count(ResourceType.RED) == 0, "Should have 0 red"
    assert player.resource_count(ResourceType.BLUE) == 0, "Should have 0 blue"
    print("  Convert ability works correctly")


def test_variable_payment_ability():
    """Test variable payment ability (Prism: pay X of one color -> gain X of different color)."""
    print("=== Test: Variable payment ability (Prism) ===")
    game = create_new_game(2)
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})
    game.draft_state = None

    player = game.players[0]

    prism = next(c for c in ARTIFACTS if c.name == "Prism")
    player.artifacts = [ControlledCard(prism)]
    player.resources = {ResourceType.RED: 5, ResourceType.BLUE: 1}

    # Use Prism's second ability: pay 3 red, gain 3 blue
    result = use_ability(game, 0, "Prism", 1,
                        cost_choices={'variable_payment': {'red': 3}},
                        effect_choices={'resource_choices': {'blue': 3}})

    assert result['success'], f"Ability should succeed: {result}"
    assert player.resource_count(ResourceType.RED) == 2, "Should have 2 red (5-3)"
    assert player.resource_count(ResourceType.BLUE) == 4, "Should have 4 blue (1+3)"
    print("  Variable payment ability works correctly")


def test_variable_payment_different_from_paid():
    """Test that different_from_paid constraint blocks same type."""
    print("=== Test: Variable payment different_from_paid constraint ===")
    game = create_new_game(2)
    game.phase = GamePhase.PLAYING
    game.action_state = ActionPhaseState(current_player=0, passed={0: False, 1: False})
    game.draft_state = None

    player = game.players[0]

    prism = next(c for c in ARTIFACTS if c.name == "Prism")
    player.artifacts = [ControlledCard(prism)]
    player.resources = {ResourceType.RED: 5}

    # Try to pay red and gain red - should be blocked, defaults to blue
    result = use_ability(game, 0, "Prism", 1,
                        cost_choices={'variable_payment': {'red': 3}},
                        effect_choices={'resource_choices': {'red': 3}})

    assert result['success'], f"Ability should succeed: {result}"
    assert player.resource_count(ResourceType.RED) == 2, "Should have 2 red (5-3)"
    # Should have gained a non-red type (defaults to blue)
    total_non_red = (player.resource_count(ResourceType.BLUE) +
                     player.resource_count(ResourceType.GREEN) +
                     player.resource_count(ResourceType.BLACK))
    assert total_non_red == 3, "Should have gained 3 of non-red type"
    print("  different_from_paid constraint works correctly")


def run_all_tests():
    """Run all ability tests."""
    print("\n" + "="*60)
    print("ABILITY SYSTEM TESTS")
    print("="*60 + "\n")

    test_tap_ability()
    test_add_to_card_ability()
    test_attack_ability()
    test_tap_another_card_cost()
    test_destroy_artifact_cost()
    test_resource_choice_effect()
    test_passive_cost_reduction()
    test_convert_ability()
    test_variable_payment_ability()
    test_variable_payment_different_from_paid()

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
