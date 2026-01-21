"""Card definitions for Res Arcana."""

from game_state import Card, CardType, CardEffects, IncomeEffect

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
# Note: Most cards have placeholder None effects - will be filled in as we implement features
ARTIFACTS = [
    # Athanor: gain 1 gold (placeholder - actual card may differ)
    Card("Athanor", CardType.ARTIFACT, effects=income(1, 'gold')),
    Card("Bone Dragon", CardType.ARTIFACT),
    Card("Celestial Horse", CardType.ARTIFACT),
    Card("Chalice of Fire", CardType.ARTIFACT),
    Card("Chalice of Life", CardType.ARTIFACT),
    Card("Corrupt Altar", CardType.ARTIFACT),
    Card("Crypt", CardType.ARTIFACT),
    Card("Cursed Skull", CardType.ARTIFACT),
    Card("Dancing Sword", CardType.ARTIFACT),
    Card("Dragon Bridle", CardType.ARTIFACT),
    Card("Dragon Egg", CardType.ARTIFACT),
    Card("Dragon Teeth", CardType.ARTIFACT),
    Card("Dwarven Pickaxe", CardType.ARTIFACT),
    Card("Earth Dragon", CardType.ARTIFACT),
    Card("Elemental Spring", CardType.ARTIFACT),
    Card("Elvish Bow", CardType.ARTIFACT),
    Card("Fiery Whip", CardType.ARTIFACT),
    Card("Fire Dragon", CardType.ARTIFACT),
    Card("Flaming Pit", CardType.ARTIFACT),
    Card("Fountain of Youth", CardType.ARTIFACT),
    Card("Guard Dog", CardType.ARTIFACT),
    Card("Hand of Glory", CardType.ARTIFACT),
    Card("Hawk", CardType.ARTIFACT),
    # Horn of Plenty: gain any 1 non-gold (placeholder - actual card may differ)
    Card("Horn of Plenty", CardType.ARTIFACT, effects=income(1, 'red', 'blue', 'green', 'black')),
    Card("Hypnotic Basin", CardType.ARTIFACT),
    Card("Jeweled Statuette", CardType.ARTIFACT),
    Card("Magical Shard", CardType.ARTIFACT),
    Card("Mermaid", CardType.ARTIFACT),
    Card("Nightingale", CardType.ARTIFACT),
    Card("Philosopher's Stone", CardType.ARTIFACT),
    # Prism: gain blue OR green (placeholder - actual card may differ)
    Card("Prism", CardType.ARTIFACT, effects=income(1, 'blue', 'green')),
    Card("Ring of Midas", CardType.ARTIFACT),
    Card("Sacrificial Dagger", CardType.ARTIFACT),
    Card("Sea Serpent", CardType.ARTIFACT),
    Card("Treant", CardType.ARTIFACT),
    Card("Tree of Life", CardType.ARTIFACT),
    Card("Vault", CardType.ARTIFACT),
    Card("Water Dragon", CardType.ARTIFACT),
    Card("Wind Dragon", CardType.ARTIFACT),
    Card("Windup Man", CardType.ARTIFACT),
    Card("Chaos Imp", CardType.ARTIFACT),
    Card("Cursed Dwarven King", CardType.ARTIFACT),
    Card("Golden Lion", CardType.ARTIFACT),
    Card("Homunculus", CardType.ARTIFACT),
    Card("Hound of Death", CardType.ARTIFACT),
    Card("Infernal Engine", CardType.ARTIFACT),
    Card("Possessed Demon Slayer", CardType.ARTIFACT),
    Card("Prismatic Dragon", CardType.ARTIFACT),
    Card("Shadowy Figure", CardType.ARTIFACT),
    Card("Vial of Light", CardType.ARTIFACT),
    Card("Vortex of Destruction", CardType.ARTIFACT),
    Card("Fire Demon", CardType.ARTIFACT),
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
PLACES_OF_POWER_PAIRS = [
    (Card("Alchemist's Tower", CardType.PLACE_OF_POWER),
     Card("Sacred Grove", CardType.PLACE_OF_POWER)),
    (Card("Catacombs of the Dead", CardType.PLACE_OF_POWER),
     Card("Sacrificial Pit", CardType.PLACE_OF_POWER)),
    (Card("Coral Castle", CardType.PLACE_OF_POWER),
     Card("Sunken Reef", CardType.PLACE_OF_POWER)),
    (Card("Cursed Forge", CardType.PLACE_OF_POWER),
     Card("Dwarven Mines", CardType.PLACE_OF_POWER)),
    (Card("Dragon's Lair", CardType.PLACE_OF_POWER),
     Card("Sorcerer's Bestiary", CardType.PLACE_OF_POWER)),
    (Card("Crystal Keep", CardType.PLACE_OF_POWER),
     Card("Dragon Aerie", CardType.PLACE_OF_POWER)),
    (Card("Gate of Hell", CardType.PLACE_OF_POWER),
     Card("Temple of the Abyss", CardType.PLACE_OF_POWER)),
]

# Flat list for convenience (but use PLACES_OF_POWER_PAIRS for proper selection)
ALL_PLACES_OF_POWER = [card for pair in PLACES_OF_POWER_PAIRS for card in pair]
