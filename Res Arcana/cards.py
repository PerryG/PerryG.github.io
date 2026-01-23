"""Card definitions for Res Arcana."""

from game_state import Card, CardType, CardEffects, IncomeEffect


def cost(**resources) -> CardEffects:
    """Create a cost effect.

    Examples:
        cost(red=2)              → costs 2 red
        cost(red=1, black=1)     → costs 1 red and 1 black
        cost(any=3)              → costs 3 of any non-gold essence
        cost(gold=2, any=1)      → costs 2 gold and 1 of any non-gold
    """
    return CardEffects(cost=resources)


def effects(cost_dict=None, income_effect=None) -> CardEffects:
    """Create a CardEffects with both cost and income."""
    return CardEffects(
        cost=cost_dict,
        income=income_effect
    )


# Helper function to create income effects
def income(count: int, *types: str) -> CardEffects:
    """Create an income effect.

    Examples:
        income(1, 'green')           → gain 1 green (fixed)
        income(1, 'black', 'green')  → gain 1 black OR green
        income(2, 'red', 'blue')     → gain 2 from red/blue in any combination
        income(3, 'red', 'blue', 'green', 'black')  → gain 3 of any non-gold
    """
    return CardEffects(income=IncomeEffect(count=count, types=list(types)))


# Artifacts - 52 total (40 base game + 12 expansion)
ARTIFACTS = [
    # Athanor: cost 1 gold + 1 red, gain 1 gold income
    Card("Athanor", CardType.ARTIFACT, effects=effects({'gold': 1, 'red': 1}, IncomeEffect(1, ['gold']))),
    Card("Bone Dragon", CardType.ARTIFACT, effects=cost(black=4, green=1)),
    Card("Celestial Horse", CardType.ARTIFACT, effects=cost(blue=2, red=1)),
    Card("Chalice of Fire", CardType.ARTIFACT, effects=cost(gold=1, red=1)),
    Card("Chalice of Life", CardType.ARTIFACT, effects=cost(blue=1, green=1, gold=1)),
    Card("Corrupt Altar", CardType.ARTIFACT, effects=cost(black=2, any=3)),
    Card("Crypt", CardType.ARTIFACT, effects=cost(black=2, any=3)),
    Card("Cursed Skull", CardType.ARTIFACT, effects=cost(black=2)),
    Card("Dancing Sword", CardType.ARTIFACT, effects=cost(gold=1, red=1)),
    Card("Dragon Bridle", CardType.ARTIFACT, effects=cost(blue=1, green=1, red=1, black=1)),
    Card("Dragon Egg", CardType.ARTIFACT, effects=cost(gold=1)),
    Card("Dragon Teeth", CardType.ARTIFACT, effects=cost(red=1, black=1)),
    Card("Dwarven Pickaxe", CardType.ARTIFACT, effects=cost(red=1)),
    Card("Earth Dragon", CardType.ARTIFACT, effects=cost(red=4, green=3)),
    Card("Elemental Spring", CardType.ARTIFACT, effects=cost(red=2, blue=1, green=1)),
    Card("Elvish Bow", CardType.ARTIFACT, effects=cost(red=2, green=1)),
    Card("Fiery Whip", CardType.ARTIFACT, effects=cost(red=2, black=2)),
    Card("Fire Dragon", CardType.ARTIFACT, effects=cost(red=6)),
    Card("Flaming Pit", CardType.ARTIFACT, effects=cost(red=2)),
    Card("Fountain of Youth", CardType.ARTIFACT, effects=cost(blue=1, black=1)),
    Card("Guard Dog", CardType.ARTIFACT, effects=cost(red=1)),
    Card("Hand of Glory", CardType.ARTIFACT, effects=cost(green=1, black=1)),
    Card("Hawk", CardType.ARTIFACT, effects=cost(blue=1, green=1)),
    # Horn of Plenty: cost 2 gold, gain any 1 non-gold
    Card("Horn of Plenty", CardType.ARTIFACT, effects=effects({'gold': 2}, IncomeEffect(1, ['red', 'blue', 'green', 'black']))),
    Card("Hypnotic Basin", CardType.ARTIFACT, effects=cost(blue=2, red=1, black=1)),
    Card("Jeweled Statuette", CardType.ARTIFACT, effects=cost(black=2, gold=1)),
    Card("Magical Shard", CardType.ARTIFACT),  # Cost: 0
    Card("Mermaid", CardType.ARTIFACT, effects=cost(blue=2, green=2)),
    Card("Nightingale", CardType.ARTIFACT, effects=cost(blue=1, green=1)),
    Card("Philosopher's Stone", CardType.ARTIFACT, effects=cost(blue=2, green=2, black=2, red=2)),
    # Prism: cost 0, gain blue OR green
    Card("Prism", CardType.ARTIFACT, effects=effects(None, IncomeEffect(1, ['blue', 'green']))),
    Card("Ring of Midas", CardType.ARTIFACT, effects=cost(green=1, gold=1)),
    Card("Sacrificial Dagger", CardType.ARTIFACT, effects=cost(black=1, gold=1)),
    Card("Sea Serpent", CardType.ARTIFACT, effects=cost(blue=6, green=3)),
    Card("Treant", CardType.ARTIFACT, effects=cost(green=3, red=2)),
    Card("Tree of Life", CardType.ARTIFACT, effects=cost(green=1, any=2)),
    Card("Vault", CardType.ARTIFACT, effects=cost(gold=1, any=1)),
    Card("Water Dragon", CardType.ARTIFACT, effects=cost(blue=6)),
    Card("Wind Dragon", CardType.ARTIFACT, effects=cost(blue=4, any=4)),
    Card("Windup Man", CardType.ARTIFACT, effects=cost(red=1, green=1, blue=1, gold=1)),
    Card("Chaos Imp", CardType.ARTIFACT, effects=cost(black=1, red=1)),
    Card("Cursed Dwarven King", CardType.ARTIFACT, effects=cost(black=1, green=1)),
    Card("Golden Lion", CardType.ARTIFACT, effects=cost(red=2, green=1, blue=1, gold=1)),
    Card("Homunculus", CardType.ARTIFACT, effects=cost(green=1)),
    Card("Hound of Death", CardType.ARTIFACT, effects=cost(green=3, black=2)),
    Card("Infernal Engine", CardType.ARTIFACT, effects=cost(black=1)),
    Card("Possessed Demon Slayer", CardType.ARTIFACT, effects=cost(black=1, red=1, gold=1)),
    Card("Prismatic Dragon", CardType.ARTIFACT, effects=cost(green=2, blue=2, red=2)),
    Card("Shadowy Figure", CardType.ARTIFACT, effects=cost(blue=2, black=2)),
    Card("Vial of Light", CardType.ARTIFACT),  # Cost: 0
    Card("Vortex of Destruction", CardType.ARTIFACT, effects=cost(green=2, red=2, black=1)),
    Card("Fire Demon", CardType.ARTIFACT, effects=cost(red=2, black=2)),
]

# Mages - 14 total (10 in base game + 4 in expansion, but we include all)
# Note: Most mages have placeholder None effects - will be filled in as we implement features
MAGES = [
    # Alchemist: gain 1 gold (placeholder - actual card may differ)
    Card("Alchemist", CardType.MAGE, effects=income(1, 'gold')),
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

# Monuments - 14 total
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

# Magic Items - 10 total
MAGIC_ITEMS = [
    Card("Alchemy", CardType.MAGIC_ITEM),
    Card("Calm | Elan", CardType.MAGIC_ITEM, effects=income(1, 'blue', 'red')),
    Card("Death | Life", CardType.MAGIC_ITEM, effects=income(1, 'green', 'black')),
    Card("Divination", CardType.MAGIC_ITEM),
    Card("Protection", CardType.MAGIC_ITEM),
    Card("Reanimate", CardType.MAGIC_ITEM),
    Card("Research", CardType.MAGIC_ITEM),
    Card("Transmutation", CardType.MAGIC_ITEM),
    Card("Illusion", CardType.MAGIC_ITEM),
    Card("Inscription", CardType.MAGIC_ITEM),
]

# Scrolls - 8 total
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

# Places of Power - 7 double-sided physical cards = 14 places total
# Each tuple represents a physical card: (front_side, back_side)
# When selecting, if you pick one side, the other becomes unavailable
# Places of Power cost various resources to acquire
PLACES_OF_POWER_PAIRS = [
    (Card("Alchemist's Tower", CardType.PLACE_OF_POWER, effects=cost(gold=3)),
     Card("Sacred Grove", CardType.PLACE_OF_POWER, effects=cost(green=8, blue=4))),
    (Card("Catacombs of the Dead", CardType.PLACE_OF_POWER, effects=cost(black=9)),
     Card("Sacrificial Pit", CardType.PLACE_OF_POWER, effects=cost(red=8, black=4))),
    (Card("Coral Castle", CardType.PLACE_OF_POWER, effects=cost(green=5, blue=5, red=5)),
     Card("Sunken Reef", CardType.PLACE_OF_POWER, effects=cost(blue=5, green=2, red=2))),
    (Card("Cursed Forge", CardType.PLACE_OF_POWER, effects=cost(red=6, black=3)),
     Card("Dwarven Mines", CardType.PLACE_OF_POWER, effects=cost(red=4, green=2, gold=1))),
    (Card("Dragon's Lair", CardType.PLACE_OF_POWER, effects=cost(green=3, blue=3, red=3, black=3)),
     Card("Sorcerer's Bestiary", CardType.PLACE_OF_POWER, effects=cost(green=4, red=2, blue=2, black=2))),
    (Card("Crystal Keep", CardType.PLACE_OF_POWER, effects=cost(gold=4, red=4, blue=4, green=4, black=4)),
     Card("Dragon Aerie", CardType.PLACE_OF_POWER, effects=cost(red=8, green=4))),
    (Card("Gate of Hell", CardType.PLACE_OF_POWER, effects=cost(red=6, black=3)),
     Card("Temple of the Abyss", CardType.PLACE_OF_POWER, effects=cost(blue=6, black=3))),
]

# Flat list for convenience (but use PLACES_OF_POWER_PAIRS for proper selection)
ALL_PLACES_OF_POWER = [card for pair in PLACES_OF_POWER_PAIRS for card in pair]
