"""Card definitions for Res Arcana.

Currently using placeholder names. These will be replaced with actual card names later.
"""

from game_state import Card, CardType

# Artifacts - 40 in base game
ARTIFACTS = [Card(f"Artifact {i}", CardType.ARTIFACT) for i in range(1, 41)]

# Mages - 10 in base game
MAGES = [Card(f"Mage {i}", CardType.MAGE) for i in range(1, 11)]

# Monuments - 10 in base game
MONUMENTS = [Card(f"Monument {i}", CardType.MONUMENT) for i in range(1, 11)]

# Magic Items - 8 in base game
MAGIC_ITEMS = [Card(f"Magic Item {i}", CardType.MAGIC_ITEM) for i in range(1, 9)]

# Scrolls - 8 (from expansion, but included)
SCROLLS = [Card(f"Scroll {i}", CardType.SCROLL) for i in range(1, 9)]

# Places of Power - 6 double-sided physical cards = 12 places total
# Each tuple represents a physical card: (front_side, back_side)
# When selecting, if you pick one side, the other becomes unavailable
# Need at least 6 cards for 4-player games (player_count + 2 = 6)
PLACES_OF_POWER_PAIRS = [
    (Card("Place of Power 1A", CardType.PLACE_OF_POWER),
     Card("Place of Power 1B", CardType.PLACE_OF_POWER)),
    (Card("Place of Power 2A", CardType.PLACE_OF_POWER),
     Card("Place of Power 2B", CardType.PLACE_OF_POWER)),
    (Card("Place of Power 3A", CardType.PLACE_OF_POWER),
     Card("Place of Power 3B", CardType.PLACE_OF_POWER)),
    (Card("Place of Power 4A", CardType.PLACE_OF_POWER),
     Card("Place of Power 4B", CardType.PLACE_OF_POWER)),
    (Card("Place of Power 5A", CardType.PLACE_OF_POWER),
     Card("Place of Power 5B", CardType.PLACE_OF_POWER)),
    (Card("Place of Power 6A", CardType.PLACE_OF_POWER),
     Card("Place of Power 6B", CardType.PLACE_OF_POWER)),
]

# Flat list for convenience (but use PLACES_OF_POWER_PAIRS for proper selection)
ALL_PLACES_OF_POWER = [card for pair in PLACES_OF_POWER_PAIRS for card in pair]
