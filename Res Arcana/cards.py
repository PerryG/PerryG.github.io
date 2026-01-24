"""Card definitions for Res Arcana."""

from game_state import (
    Card, CardType, CardEffects, IncomeEffect,
    Ability, AbilityCost, AbilityEffect, PassiveEffect
)


# ============================================================
# Helper functions for creating card effects
# ============================================================

def cost(**resources) -> CardEffects:
    """Create a CardEffects with just a cost."""
    return CardEffects(cost=resources)


def income_effect(count: int, *types: str, conditional: bool = False, add_to_card: bool = False) -> IncomeEffect:
    """Create an IncomeEffect."""
    return IncomeEffect(count=count, types=list(types), conditional=conditional, add_to_card=add_to_card)


# ============================================================
# Helper functions for creating abilities
# ============================================================

def tap_cost() -> AbilityCost:
    """Cost: tap this card."""
    return AbilityCost(cost_type='tap')


def pay_cost(**resources) -> AbilityCost:
    """Cost: pay resources from player pool."""
    return AbilityCost(cost_type='pay', resources=resources)


def remove_from_card_cost(**resources) -> AbilityCost:
    """Cost: remove resources from this card."""
    return AbilityCost(cost_type='remove_from_card', resources=resources)


def destroy_self_cost() -> AbilityCost:
    """Cost: destroy this card."""
    return AbilityCost(cost_type='destroy_self')


def destroy_artifact_cost(must_be_different: bool = True) -> AbilityCost:
    """Cost: destroy an artifact."""
    return AbilityCost(cost_type='destroy_artifact', must_be_different=must_be_different)


def discard_cost() -> AbilityCost:
    """Cost: discard a card from hand."""
    return AbilityCost(cost_type='discard')


def tap_card_cost(tag: str = None) -> AbilityCost:
    """Cost: tap another card (optionally filtered by tag)."""
    return AbilityCost(cost_type='tap_card', tag=tag)


def gain_effect(**resources) -> AbilityEffect:
    """Effect: gain specific resources to player pool."""
    return AbilityEffect(effect_type='gain', resources=resources)


def gain_choice_effect(count: int, *types: str) -> AbilityEffect:
    """Effect: gain resources with choice."""
    return AbilityEffect(effect_type='gain', count=count, types=list(types))


def add_to_card_effect(**resources) -> AbilityEffect:
    """Effect: add specific resources to this card."""
    return AbilityEffect(effect_type='add_to_card', resources=resources)


def add_to_card_choice_effect(count: int, *types: str) -> AbilityEffect:
    """Effect: add resources to this card with choice."""
    return AbilityEffect(effect_type='add_to_card', count=count, types=list(types))


def add_to_other_card_effect(resource_type: str) -> AbilityEffect:
    """Effect: add a resource to another card."""
    return AbilityEffect(effect_type='add_to_card', target='other', resources={resource_type: 1})


def take_from_card_effect() -> AbilityEffect:
    """Effect: take all resources from another card."""
    return AbilityEffect(effect_type='take_from_card', target='other')


def attack_effect(green_cost: int, avoid_cost=None) -> AbilityEffect:
    """Effect: attack all opponents."""
    return AbilityEffect(effect_type='attack', green_cost=green_cost, avoid_cost=avoid_cost)


def draw_effect(count: int = 1) -> AbilityEffect:
    """Effect: draw cards."""
    return AbilityEffect(effect_type='draw', count=count)


def draw_discard_effect(draw: int, discard: int) -> AbilityEffect:
    """Effect: draw cards then discard."""
    return AbilityEffect(effect_type='draw_discard', count=draw, discard_count=discard)


def untap_effect(target: str = 'other') -> AbilityEffect:
    """Effect: untap a card."""
    return AbilityEffect(effect_type='untap', target=target)


def convert_effect() -> AbilityEffect:
    """Effect: convert resources to gold."""
    return AbilityEffect(effect_type='convert')


def play_card_effect(source: str = 'hand', discount: int = 0, discount_type: str = 'non_gold',
                     free: bool = False, card_filter: str = None) -> AbilityEffect:
    """Effect: play a card from hand or discard."""
    return AbilityEffect(effect_type='play_card', source=source, discount=discount,
                         discount_type=discount_type, free=free, card_filter=card_filter)


def give_opponents_effect(**resources) -> AbilityEffect:
    """Effect: give resources to all opponents."""
    return AbilityEffect(effect_type='give_opponents', resources=resources)


def gain_per_opponent_effect(gain_type: str, check_type: str) -> AbilityEffect:
    """Effect: gain resources equal to max of a resource type among opponents."""
    return AbilityEffect(effect_type='gain_per_opponent', resources={gain_type: 1}, check_resource=check_type)


def gain_per_opponent_count_effect(gain_type: str, check_tag: str) -> AbilityEffect:
    """Effect: gain resources equal to max count of a card type among opponents."""
    return AbilityEffect(effect_type='gain_per_opponent_count', resources={gain_type: 1}, check_tag=check_tag)


def reorder_deck_effect(count: int, deck: str = 'self') -> AbilityEffect:
    """Effect: look at and reorder top cards of a deck."""
    return AbilityEffect(effect_type='reorder_deck', count=count, deck=deck)


def ignore_attack_effect() -> AbilityEffect:
    """Effect: ignore the attack (for reactions)."""
    return AbilityEffect(effect_type='ignore_attack')


def ability(costs: list, effects: list) -> Ability:
    """Create an ability with costs and effects."""
    return Ability(costs=costs, effects=effects)


def reaction(trigger: str, costs: list, effects: list, trigger_filter: str = None) -> Ability:
    """Create a reaction ability."""
    return Ability(costs=costs, effects=effects, trigger=trigger, trigger_filter=trigger_filter)


def passive(effect_type: str, **kwargs) -> PassiveEffect:
    """Create a passive effect."""
    return PassiveEffect(effect_type=effect_type, **kwargs)


# ============================================================
# Artifacts - 52 total (40 base game + 12 expansion)
# ============================================================

ARTIFACTS = [
    # Athanor: cost gold+red
    # Ability 1: tap+red → add 2 red to card
    # Ability 2: tap+remove 6 red from card → convert any resources of one color to gold
    Card("Athanor", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'gold': 1, 'red': 1},
             abilities=[
                 ability([tap_cost(), pay_cost(red=1)], [add_to_card_effect(red=2)]),
                 ability([tap_cost(), remove_from_card_cost(red=6)], [convert_effect()]),
             ]
         )),

    # Bone Dragon: dragon, 1 pt, tap → attack 2 green (avoid: 1 black)
    Card("Bone Dragon", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'black': 4, 'green': 1},
             abilities=[
                 ability([tap_cost()], [attack_effect(2, {'black': 1})]),
             ]
         ),
         tags={'dragon'}, points=1),

    # Celestial Horse: animal, income 2 from red/blue/green
    Card("Celestial Horse", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 2, 'red': 1},
             income=income_effect(2, 'red', 'blue', 'green'),
         ),
         tags={'animal'}),

    # Chalice of Fire: income 2 red, tap+red → untap another card
    Card("Chalice of Fire", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'gold': 1, 'red': 1},
             income=income_effect(2, 'red'),
             abilities=[
                 ability([tap_cost(), pay_cost(red=1)], [untap_effect('other')]),
             ]
         )),

    # Chalice of Life: income 1 blue + 1 green, pay 2 blue → add 2 blue + 1 green to card
    Card("Chalice of Life", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 1, 'green': 1, 'gold': 1},
             income=income_effect(1, 'blue', 'green'),  # Note: this is 1 blue AND 1 green, not choice
             abilities=[
                 ability([pay_cost(blue=2)], [add_to_card_effect(blue=2, green=1)]),
             ]
         )),

    # Corrupt Altar: income 1 green + 1 black
    # Ability 1: pay 2 green → add 3 red to card
    # Ability 2: tap+destroy artifact → gain 2+cost non-gold
    Card("Corrupt Altar", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'black': 2, 'any': 3},
             income=income_effect(1, 'green', 'black'),
             abilities=[
                 ability([pay_cost(green=2)], [add_to_card_effect(red=3)]),
                 ability([tap_cost(), destroy_artifact_cost(must_be_different=False)],
                        [AbilityEffect(effect_type='gain_from_destroyed', bonus=2)]),
             ]
         )),

    # Crypt: tap → 2 black, tap+1 black → play from discard with 2 non-gold discount
    Card("Crypt", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'black': 2, 'any': 3},
             abilities=[
                 ability([tap_cost()], [gain_effect(black=2)]),
                 ability([tap_cost(), pay_cost(black=1)],
                        [play_card_effect(source='discard', discount=2, discount_type='non_gold')]),
             ]
         )),

    # Cursed Skull: tap+1 green → add 3 non-gold non-green to card
    Card("Cursed Skull", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'black': 2},
             abilities=[
                 ability([tap_cost(), pay_cost(green=1)],
                        [add_to_card_choice_effect(3, 'red', 'blue', 'black')]),
             ]
         )),

    # Dancing Sword: income 1 black + 1 red
    # Reaction attacked: pay red → ignore attack + add black to card
    Card("Dancing Sword", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'gold': 1, 'red': 1},
             income=income_effect(1, 'black', 'red'),
             abilities=[
                 reaction('attacked', [pay_cost(red=1)], [ignore_attack_effect(), add_to_card_effect(black=1)]),
             ]
         )),

    # Dragon Bridle: 1 pt
    # Passive: dragons cost 3 less non-gold
    # Reaction attacked by dragon: tap → ignore
    Card("Dragon Bridle", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 1, 'green': 1, 'red': 1, 'black': 1},
             passives=[passive('cost_reduction', card_filter='dragon', amount=3, reduction_type='non_gold')],
             abilities=[
                 reaction('attacked', [tap_cost()], [ignore_attack_effect()], trigger_filter='dragon'),
             ]
         ),
         points=1),

    # Dragon Egg: 1 pt, destroy self → play dragon with 4 non-gold discount
    Card("Dragon Egg", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'gold': 1},
             abilities=[
                 ability([destroy_self_cost()],
                        [play_card_effect(source='hand', discount=4, discount_type='non_gold', card_filter='dragon')]),
             ]
         ),
         points=1),

    # Dragon Teeth: pay 2 red → add 3 red to card, tap+3 red → play dragon free
    Card("Dragon Teeth", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 1, 'black': 1},
             abilities=[
                 ability([pay_cost(red=2)], [add_to_card_effect(red=3)]),
                 ability([tap_cost(), pay_cost(red=3)],
                        [play_card_effect(source='hand', free=True, card_filter='dragon')]),
             ]
         )),

    # Dwarven Pickaxe: tap+1 red → 1 gold
    Card("Dwarven Pickaxe", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 1},
             abilities=[
                 ability([tap_cost(), pay_cost(red=1)], [gain_effect(gold=1)]),
             ]
         )),

    # Earth Dragon: dragon, 1 pt, tap → attack 2 green (avoid: 1 gold)
    Card("Earth Dragon", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 4, 'green': 3},
             abilities=[
                 ability([tap_cost()], [attack_effect(2, {'gold': 1})]),
             ]
         ),
         tags={'dragon'}, points=1),

    # Elemental Spring: income 1 blue+green+red, reaction attacked: pay blue → ignore
    Card("Elemental Spring", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 2, 'blue': 1, 'green': 1},
             income=income_effect(1, 'blue', 'green', 'red'),
             abilities=[
                 reaction('attacked', [pay_cost(blue=1)], [ignore_attack_effect()]),
             ]
         )),

    # Elvish Bow: tap → draw, tap → attack 1 green
    Card("Elvish Bow", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 2, 'green': 1},
             abilities=[
                 ability([tap_cost()], [draw_effect(1)]),
                 ability([tap_cost()], [attack_effect(1, None)]),
             ]
         )),

    # Fiery Whip: tap → 3 red + give opponents 1 red, tap+destroy different artifact → 2+cost non-gold
    Card("Fiery Whip", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 2, 'black': 2},
             abilities=[
                 ability([tap_cost()], [gain_effect(red=3), give_opponents_effect(red=1)]),
                 ability([tap_cost(), destroy_artifact_cost(must_be_different=True)],
                        [AbilityEffect(effect_type='gain_from_destroyed', bonus=2)]),
             ]
         )),

    # Fire Dragon: dragon, 1 pt, tap → attack 2 green (avoid: 1 blue)
    Card("Fire Dragon", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 6},
             abilities=[
                 ability([tap_cost()], [attack_effect(2, {'blue': 1})]),
             ]
         ),
         tags={'dragon'}, points=1),

    # Flaming Pit: income 1 red, tap+1 green → 1 red + 1 black
    Card("Flaming Pit", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 2},
             income=income_effect(1, 'red'),
             abilities=[
                 ability([tap_cost(), pay_cost(green=1)], [gain_effect(red=1, black=1)]),
             ]
         )),

    # Fountain of Youth: income 1 green, pay 2 black → add 2 blue + 1 green to card
    Card("Fountain of Youth", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 1, 'black': 1},
             income=income_effect(1, 'green'),
             abilities=[
                 ability([pay_cost(black=2)], [add_to_card_effect(blue=2, green=1)]),
             ]
         )),

    # Guard Dog: animal, pay 1 red (when tapped) → untap self, reaction attacked: tap → ignore
    Card("Guard Dog", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 1},
             abilities=[
                 ability([pay_cost(red=1)], [untap_effect('self')]),  # Note: only usable when tapped
                 reaction('attacked', [tap_cost()], [ignore_attack_effect()]),
             ]
         ),
         tags={'animal'}),

    # Hand of Glory: tap → 2 black + give opponents 1 black
    Card("Hand of Glory", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'green': 1, 'black': 1},
             abilities=[
                 ability([tap_cost()], [gain_effect(black=2), give_opponents_effect(black=1)]),
             ]
         )),

    # Hawk: animal, income 1 blue, tap+2 blue → draw, tap → reorder top 3 of deck or monuments
    Card("Hawk", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 1, 'green': 1},
             income=income_effect(1, 'blue'),
             abilities=[
                 ability([tap_cost(), pay_cost(blue=2)], [draw_effect(1)]),
                 ability([tap_cost()], [reorder_deck_effect(3, 'self_or_monuments')]),
             ]
         ),
         tags={'animal'}),

    # Horn of Plenty: tap → 1 gold, tap → 3 non-gold
    Card("Horn of Plenty", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'gold': 2},
             abilities=[
                 ability([tap_cost()], [gain_effect(gold=1)]),
                 ability([tap_cost()], [gain_choice_effect(3, 'red', 'blue', 'green', 'black')]),
             ]
         )),

    # Hypnotic Basin: income 2 blue, tap → gain blue equal to max red among opponents
    Card("Hypnotic Basin", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 2, 'red': 1, 'black': 1},
             income=income_effect(2, 'blue'),
             abilities=[
                 ability([tap_cost()], [gain_per_opponent_effect('blue', 'red')]),
             ]
         )),

    # Jeweled Statuette: 1 pt, tap → 3 black + give opponents 1 black, destroy self → 2 gold + 1 red
    Card("Jeweled Statuette", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'black': 2, 'gold': 1},
             abilities=[
                 ability([tap_cost()], [gain_effect(black=3), give_opponents_effect(black=1)]),
                 ability([destroy_self_cost()], [gain_effect(gold=2, red=1)]),
             ]
         ),
         points=1),

    # Magical Shard: tap → 1 non-gold
    Card("Magical Shard", CardType.ARTIFACT,
         effects=CardEffects(
             abilities=[
                 ability([tap_cost()], [gain_choice_effect(1, 'red', 'blue', 'green', 'black')]),
             ]
         )),

    # Mermaid: animal, income 1 blue, tap+pay 1 blue/green/gold → put that resource on another card
    Card("Mermaid", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 2, 'green': 2},
             income=income_effect(1, 'blue'),
             abilities=[
                 # Three separate abilities for each resource type
                 ability([tap_cost(), pay_cost(blue=1)], [add_to_other_card_effect('blue')]),
                 ability([tap_cost(), pay_cost(green=1)], [add_to_other_card_effect('green')]),
                 ability([tap_cost(), pay_cost(gold=1)], [add_to_other_card_effect('gold')]),
             ]
         ),
         tags={'animal'}),

    # Nightingale: animal, 1 pt (no abilities)
    Card("Nightingale", CardType.ARTIFACT,
         effects=CardEffects(cost={'blue': 1, 'green': 1}),
         tags={'animal'}, points=1),

    # Philosopher's Stone: 1 pt, tap+2 any → convert any resources of one color to gold
    Card("Philosopher's Stone", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 2, 'green': 2, 'black': 2, 'red': 2},
             abilities=[
                 ability([tap_cost(), pay_cost(any=2)], [convert_effect()]),
             ]
         ),
         points=1),

    # Prism: tap+1 any → 2 non-gold, tap+X of one → X of different non-gold
    Card("Prism", CardType.ARTIFACT,
         effects=CardEffects(
             abilities=[
                 ability([tap_cost(), pay_cost(any=1)], [gain_choice_effect(2, 'red', 'blue', 'green', 'black')]),
                 ability([tap_cost()], [AbilityEffect(effect_type='exchange', target='non_gold')]),
             ]
         )),

    # Ring of Midas: 1 pt, tap → add gold to card, pay 2 green → add gold to card
    Card("Ring of Midas", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'green': 1, 'gold': 1},
             abilities=[
                 ability([tap_cost()], [add_to_card_effect(gold=1)]),
                 ability([pay_cost(green=2)], [add_to_card_effect(gold=1)]),
             ]
         ),
         points=1),

    # Sacrificial Dagger: tap+1 green → add 3 black to card,
    # tap+destroy self+discard → gain non-gold equal to discarded card's cost
    Card("Sacrificial Dagger", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'black': 1, 'gold': 1},
             abilities=[
                 ability([tap_cost(), pay_cost(green=1)], [add_to_card_effect(black=3)]),
                 ability([tap_cost(), destroy_self_cost(), discard_cost()],
                        [AbilityEffect(effect_type='gain_from_discarded')]),
             ]
         )),

    # Sea Serpent: dragon+animal, 1 pt, tap → attack 2 green (avoid: destroy own artifact)
    Card("Sea Serpent", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 6, 'green': 3},
             abilities=[
                 ability([tap_cost()], [attack_effect(2, {'destroy_artifact': True})]),
             ]
         ),
         tags={'dragon', 'animal'}, points=1),

    # Treant: animal, income 2 green, tap → gain red equal to max black among opponents
    Card("Treant", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'green': 3, 'red': 2},
             income=income_effect(2, 'green'),
             abilities=[
                 ability([tap_cost()], [gain_per_opponent_effect('red', 'black')]),
             ]
         ),
         tags={'animal'}),

    # Tree of Life: tap → 3 green + give opponents 1 green, reaction attacked: pay green → ignore
    Card("Tree of Life", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'green': 1, 'any': 2},
             abilities=[
                 ability([tap_cost()], [gain_effect(green=3), give_opponents_effect(green=1)]),
                 reaction('attacked', [pay_cost(green=1)], [ignore_attack_effect()]),
             ]
         )),

    # Vault: tap → add gold to card, conditional income: if gold left on card, gain 2 non-gold
    Card("Vault", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'gold': 1, 'any': 1},
             income=income_effect(2, 'red', 'blue', 'green', 'black', conditional=True),
             abilities=[
                 ability([tap_cost()], [add_to_card_effect(gold=1)]),
             ]
         )),

    # Water Dragon: dragon, 1 pt, tap → attack 2 green (avoid: 1 red)
    Card("Water Dragon", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 6},
             abilities=[
                 ability([tap_cost()], [attack_effect(2, {'red': 1})]),
             ]
         ),
         tags={'dragon'}, points=1),

    # Wind Dragon: dragon, 1 pt, tap → attack 2 green (avoid: discard a card)
    Card("Wind Dragon", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 4, 'any': 4},
             abilities=[
                 ability([tap_cost()], [attack_effect(2, {'discard': True})]),
             ]
         ),
         tags={'dragon'}, points=1),

    # Windup Man: tap → add 1 any to card
    # Conditional income: if resources left, add 2 of each type on card
    Card("Windup Man", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 1, 'green': 1, 'blue': 1, 'gold': 1},
             income=income_effect(2, 'red', 'blue', 'green', 'black', 'gold',
                                  conditional=True, add_to_card=True),
             abilities=[
                 ability([tap_cost()], [add_to_card_choice_effect(1, 'red', 'blue', 'green', 'black', 'gold')]),
             ]
         )),

    # Chaos Imp: demon, tap+1 green → untap another demon, pay black+red → add 3 black to card
    Card("Chaos Imp", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'black': 1, 'red': 1},
             abilities=[
                 ability([tap_cost(), pay_cost(green=1)], [untap_effect('demon')]),
                 ability([pay_cost(black=1, red=1)], [add_to_card_effect(black=3)]),
             ]
         ),
         tags={'demon'}),

    # Cursed Dwarven King: demon, pay black+red+green → add 2 gold to card, tap+tap dragon → 1 gold
    Card("Cursed Dwarven King", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'black': 1, 'green': 1},
             abilities=[
                 ability([pay_cost(black=1, red=1, green=1)], [add_to_card_effect(gold=2)]),
                 ability([tap_cost(), tap_card_cost('dragon')], [gain_effect(gold=1)]),
             ]
         ),
         tags={'demon'}),

    # Golden Lion: animal, 1 pt, income blue+green+red, reaction attacked: tap → ignore
    Card("Golden Lion", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 2, 'green': 1, 'blue': 1, 'gold': 1},
             income=income_effect(1, 'blue', 'green', 'red'),
             abilities=[
                 reaction('attacked', [tap_cost()], [ignore_attack_effect()]),
             ]
         ),
         tags={'animal'}, points=1),

    # Homunculus: demon, tap → add 2 non-gold to card, passive: demons cost 2 less (any)
    Card("Homunculus", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'green': 1},
             passives=[passive('cost_reduction', card_filter='demon', amount=2, reduction_type='any')],
             abilities=[
                 ability([tap_cost()], [add_to_card_choice_effect(2, 'red', 'blue', 'green', 'black')]),
             ]
         ),
         tags={'demon'}),

    # Hound of Death: demon+animal, income 2 black
    # tap+1 green → attack 2 green, tap → gain black equal to max gold among opponents
    Card("Hound of Death", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'green': 3, 'black': 2},
             income=income_effect(2, 'black'),
             abilities=[
                 ability([tap_cost(), pay_cost(green=1)], [attack_effect(2, None)]),
                 ability([tap_cost()], [gain_per_opponent_effect('black', 'gold')]),
             ]
         ),
         tags={'demon', 'animal'}),

    # Infernal Engine: income 1 red
    # tap → take all resources from another card, tap+1 any → add that to card
    Card("Infernal Engine", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'black': 1},
             income=income_effect(1, 'red'),
             abilities=[
                 ability([tap_cost()], [take_from_card_effect()]),
                 ability([tap_cost(), pay_cost(any=1)],
                        [AbilityEffect(effect_type='add_paid_to_card')]),
             ]
         )),

    # Possessed Demon Slayer: demon, 1 pt
    # tap → gain red equal to max demons among opponents, reaction attacked by demon: ignore (no cost)
    Card("Possessed Demon Slayer", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'black': 1, 'red': 1, 'gold': 1},
             abilities=[
                 ability([tap_cost()], [gain_per_opponent_count_effect('red', 'demon')]),
                 reaction('attacked', [], [ignore_attack_effect()], trigger_filter='demon'),
             ]
         ),
         tags={'demon'}, points=1),

    # Prismatic Dragon: dragon, 1 pt, income 1 non-gold, tap+1 gold → add 4 non-gold to card
    Card("Prismatic Dragon", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'green': 2, 'blue': 2, 'red': 2},
             income=income_effect(1, 'red', 'blue', 'green', 'black'),
             abilities=[
                 ability([tap_cost(), pay_cost(gold=1)],
                        [add_to_card_choice_effect(4, 'red', 'blue', 'green', 'black')]),
             ]
         ),
         tags={'dragon'}, points=1),

    # Shadowy Figure: demon, income 1 blue
    # tap+1 green → 3 blue, tap+1 blue → draw 2 discard 1
    Card("Shadowy Figure", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'blue': 2, 'black': 2},
             income=income_effect(1, 'blue'),
             abilities=[
                 ability([tap_cost(), pay_cost(green=1)], [gain_effect(blue=3)]),
                 ability([tap_cost(), pay_cost(blue=1)],
                        [AbilityEffect(effect_type='draw_discard', count=2, discard_count=1)]),
             ]
         ),
         tags={'demon'}),

    # Vial of Light: tap+1 black → 1 green + 1 red
    # Reaction any artifact destroyed: gain 1 non-gold non-black
    Card("Vial of Light", CardType.ARTIFACT,
         effects=CardEffects(
             abilities=[
                 ability([tap_cost(), pay_cost(black=1)], [gain_effect(green=1, red=1)]),
                 reaction('artifact_destroyed', [], [gain_choice_effect(1, 'red', 'blue', 'green')]),
             ]
         )),

    # Vortex of Destruction: demon, income 1 black + 1 red
    # tap+1 green → 3 black, tap+destroy different artifact → 2+cost non-gold
    Card("Vortex of Destruction", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'green': 2, 'red': 2, 'black': 1},
             income=income_effect(1, 'black', 'red'),
             abilities=[
                 ability([tap_cost(), pay_cost(green=1)], [gain_effect(black=3)]),
                 ability([tap_cost(), destroy_artifact_cost(must_be_different=True)],
                        [AbilityEffect(effect_type='gain_from_destroyed', bonus=2)]),
             ]
         ),
         tags={'demon'}),

    # Fire Demon: demon, income 1 red, tap+1 green → 3 red, tap+1 red → attack 2 green
    Card("Fire Demon", CardType.ARTIFACT,
         effects=CardEffects(
             cost={'red': 2, 'black': 2},
             income=income_effect(1, 'red'),
             abilities=[
                 ability([tap_cost(), pay_cost(green=1)], [gain_effect(red=3)]),
                 ability([tap_cost(), pay_cost(red=1)], [attack_effect(2, None)]),
             ]
         ),
         tags={'demon'}),
]

# ============================================================
# Mages - 14 total
# ============================================================

MAGES = [
    Card("Alchemist", CardType.MAGE),
    Card("Artificer", CardType.MAGE),
    Card("Bard", CardType.MAGE),
    Card("Beastmaster", CardType.MAGE),
    Card("Demonologist", CardType.MAGE),
    Card("Diviner", CardType.MAGE),
    Card("Druid", CardType.MAGE),
    Card("Duelist", CardType.MAGE),
    Card("Healer", CardType.MAGE),
    Card("Necromancer", CardType.MAGE),
    Card("Scholar", CardType.MAGE),
    Card("Seer", CardType.MAGE),
    Card("Transmuter", CardType.MAGE),
    Card("Witch", CardType.MAGE),
]

# ============================================================
# Monuments - 14 total
# ============================================================

MONUMENTS = [
    Card("Golden Statue", CardType.MONUMENT),
    Card("Hanging Gardens", CardType.MONUMENT),
    Card("Library", CardType.MONUMENT),
    Card("Obelisk", CardType.MONUMENT),
    Card("Solomon's Mine", CardType.MONUMENT),
    Card("Colossus", CardType.MONUMENT),
    Card("Mausoleum", CardType.MONUMENT),
    Card("Oracle", CardType.MONUMENT),
    Card("Temple", CardType.MONUMENT),
    Card("Great Pyramid", CardType.MONUMENT),
    Card("Dark Cathedral", CardType.MONUMENT),
    Card("Demon Workshop", CardType.MONUMENT),
    Card("Warrior's Hall", CardType.MONUMENT),
    Card("Alchemical Lab", CardType.MONUMENT),
]

# ============================================================
# Magic Items - 10 total
# ============================================================

MAGIC_ITEMS = [
    Card("Alchemy", CardType.MAGIC_ITEM),
    Card("Calm | Elan", CardType.MAGIC_ITEM),
    Card("Death | Life", CardType.MAGIC_ITEM),
    Card("Divination", CardType.MAGIC_ITEM),
    Card("Protection", CardType.MAGIC_ITEM),
    Card("Reanimate", CardType.MAGIC_ITEM),
    Card("Research", CardType.MAGIC_ITEM),
    Card("Transmutation", CardType.MAGIC_ITEM),
    Card("Illusion", CardType.MAGIC_ITEM),
    Card("Inscription", CardType.MAGIC_ITEM),
]

# ============================================================
# Scrolls - 8 total
# ============================================================

SCROLLS = [
    Card("Augury", CardType.SCROLL),
    Card("Destruction", CardType.SCROLL),
    Card("Disjunction", CardType.SCROLL),
    Card("Projection", CardType.SCROLL),
    Card("Revivify", CardType.SCROLL),
    Card("Shield", CardType.SCROLL),
    Card("Transform", CardType.SCROLL),
    Card("Vitality", CardType.SCROLL),
]

# ============================================================
# Places of Power - 7 double-sided physical cards = 14 places total
# ============================================================

def pop_cost(**resources) -> CardEffects:
    """Create a Place of Power cost."""
    return CardEffects(cost=resources)


PLACES_OF_POWER_PAIRS = [
    (Card("Alchemist's Tower", CardType.PLACE_OF_POWER, effects=pop_cost(gold=3)),
     Card("Sacred Grove", CardType.PLACE_OF_POWER, effects=pop_cost(green=8, blue=4))),
    (Card("Catacombs of the Dead", CardType.PLACE_OF_POWER, effects=pop_cost(black=9)),
     Card("Sacrificial Pit", CardType.PLACE_OF_POWER, effects=pop_cost(red=8, black=4))),
    (Card("Coral Castle", CardType.PLACE_OF_POWER, effects=pop_cost(green=5, blue=5, red=5)),
     Card("Sunken Reef", CardType.PLACE_OF_POWER, effects=pop_cost(blue=5, green=2, red=2))),
    (Card("Cursed Forge", CardType.PLACE_OF_POWER, effects=pop_cost(red=6, black=3)),
     Card("Dwarven Mines", CardType.PLACE_OF_POWER, effects=pop_cost(red=4, green=2, gold=1))),
    (Card("Dragon's Lair", CardType.PLACE_OF_POWER, effects=pop_cost(green=3, blue=3, red=3, black=3)),
     Card("Sorcerer's Bestiary", CardType.PLACE_OF_POWER, effects=pop_cost(green=4, red=2, blue=2, black=2))),
    (Card("Crystal Keep", CardType.PLACE_OF_POWER, effects=pop_cost(gold=4, red=4, blue=4, green=4, black=4)),
     Card("Dragon Aerie", CardType.PLACE_OF_POWER, effects=pop_cost(red=8, green=4))),
    (Card("Gate of Hell", CardType.PLACE_OF_POWER, effects=pop_cost(red=6, black=3)),
     Card("Temple of the Abyss", CardType.PLACE_OF_POWER, effects=pop_cost(blue=6, black=3))),
]

# Flat list for convenience (but use PLACES_OF_POWER_PAIRS for proper selection)
ALL_PLACES_OF_POWER = [card for pair in PLACES_OF_POWER_PAIRS for card in pair]
