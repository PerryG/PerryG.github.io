from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ResourceType(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    BLACK = "black"
    GOLD = "gold"


class CardType(Enum):
    ARTIFACT = "artifact"
    PLACE_OF_POWER = "place_of_power"
    MONUMENT = "monument"
    MAGIC_ITEM = "magic_item"
    MAGE = "mage"


@dataclass
class Card:
    name: str
    card_type: CardType
    # Additional card-specific properties to be added later


@dataclass
class ControlledCard:
    """A card on the table controlled by a player."""
    card: Card
    tapped: bool = False
    resources: Dict[ResourceType, int] = field(default_factory=dict)

    def resource_count(self, resource_type: ResourceType) -> int:
        return self.resources.get(resource_type, 0)

    def add_resource(self, resource_type: ResourceType, amount: int = 1):
        self.resources[resource_type] = self.resource_count(resource_type) + amount

    def remove_resource(self, resource_type: ResourceType, amount: int = 1) -> bool:
        """Remove resources. Returns False if insufficient resources."""
        current = self.resource_count(resource_type)
        if current < amount:
            return False
        self.resources[resource_type] = current - amount
        return True


@dataclass
class PlayerState:
    player_id: int

    # Controlled cards on the table
    mage: ControlledCard
    magic_item: ControlledCard
    artifacts: List[ControlledCard] = field(default_factory=list)
    monuments: List[ControlledCard] = field(default_factory=list)
    places_of_power: List[ControlledCard] = field(default_factory=list)

    # Hand, deck, discard (artifacts only)
    hand: List[Card] = field(default_factory=list)
    deck: List[Card] = field(default_factory=list)
    discard: List[Card] = field(default_factory=list)

    # Unplaced resources (not on any card)
    resources: Dict[ResourceType, int] = field(default_factory=dict)

    # First player token
    has_first_player_token: bool = False
    first_player_token_face_up: bool = True

    def resource_count(self, resource_type: ResourceType) -> int:
        return self.resources.get(resource_type, 0)

    def add_resource(self, resource_type: ResourceType, amount: int = 1):
        self.resources[resource_type] = self.resource_count(resource_type) + amount

    def remove_resource(self, resource_type: ResourceType, amount: int = 1) -> bool:
        """Remove resources from player's unplaced pool. Returns False if insufficient."""
        current = self.resource_count(resource_type)
        if current < amount:
            return False
        self.resources[resource_type] = current - amount
        return True

    def all_controlled_cards(self) -> List[ControlledCard]:
        """Returns all cards controlled by this player."""
        return [self.mage, self.magic_item] + self.artifacts + self.monuments + self.places_of_power


@dataclass
class GameState:
    players: List[PlayerState]

    # Shared zones
    available_monuments: List[Card] = field(default_factory=list)
    available_places_of_power: List[Card] = field(default_factory=list)
    monument_deck: List[Card] = field(default_factory=list)

    def get_player(self, player_id: int) -> Optional[PlayerState]:
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def first_player(self) -> Optional[PlayerState]:
        for player in self.players:
            if player.has_first_player_token:
                return player
        return None
