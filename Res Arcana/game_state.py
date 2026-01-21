from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ResourceType(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    BLACK = "black"
    GOLD = "gold"


class GamePhase(Enum):
    # Setup phases
    SETUP = "setup"                          # Initial setup (dealing mages, artifacts)
    DRAFTING_ROUND_1 = "drafting_round_1"    # Pick 1, pass 3 clockwise
    DRAFTING_ROUND_2 = "drafting_round_2"    # Pick 1, pass 3 counter-clockwise
    MAGE_SELECTION = "mage_selection"        # Secretly pick 1 of 2 mages
    MAGIC_ITEM_SELECTION = "magic_item_selection"  # Take magic item in reverse order
    # Gameplay phases
    INCOME = "income"                        # Collect income at start of round
    PLAYING = "playing"                      # Main action phase


class CardType(Enum):
    ARTIFACT = "artifact"
    PLACE_OF_POWER = "place_of_power"
    MONUMENT = "monument"
    MAGIC_ITEM = "magic_item"
    MAGE = "mage"
    SCROLL = "scroll"


@dataclass
class IncomeEffect:
    """Represents income a card can generate each round.

    count: How many resources to gain
    types: Which resource types are allowed (e.g., ['green'], ['black', 'green'], etc.)

    Examples:
    - count=1, types=['green'] → gain 1 green (fixed)
    - count=1, types=['black', 'green'] → gain 1 black OR green
    - count=2, types=['green', 'blue', 'red'] → gain 2 from green/blue/red in any combination
    - count=3, types=['red', 'blue', 'green', 'black'] → gain 3 of any non-gold
    """
    count: int
    types: List[str]


@dataclass
class CardEffects:
    """All effects a card can have. Expandable for future abilities."""
    income: Optional[IncomeEffect] = None
    # Future: tap_ability, reaction, cost, victory_points, etc.


@dataclass
class Card:
    name: str
    card_type: CardType
    effects: Optional[CardEffects] = None


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
    scrolls: List[Card] = field(default_factory=list)  # Scrolls can't be tapped or hold resources

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
class DraftState:
    """Tracks state during the drafting phase."""
    # Cards each player is currently choosing from (indexed by player_id)
    cards_to_pick: Dict[int, List[Card]] = field(default_factory=dict)
    # Cards each player has drafted so far
    drafted_cards: Dict[int, List[Card]] = field(default_factory=dict)
    # Mage options for each player (they pick 1 of 2)
    mage_options: Dict[int, List[Card]] = field(default_factory=dict)
    # Selected mage (before reveal) - None until player selects
    selected_mage: Dict[int, Optional[Card]] = field(default_factory=dict)
    # Current player for magic item selection (reverse order)
    magic_item_selector: Optional[int] = None


@dataclass
class IncomePhaseState:
    """Tracks state during the income phase."""
    # Whether each player has finalized their income choices
    finalized: Dict[int, bool] = field(default_factory=dict)
    # Whether each player is waiting for earlier players to finalize first
    waiting_for_earlier: Dict[int, bool] = field(default_factory=dict)
    # Resource collection choices: player_id -> {card_name: take_all}
    collection_choices: Dict[int, Dict[str, bool]] = field(default_factory=dict)
    # Income choices for cards with options: player_id -> {card_name: {resource: count}}
    income_choices: Dict[int, Dict[str, Dict[str, int]]] = field(default_factory=dict)
    # Player preference: auto-skip taking resources from Places of Power
    auto_skip_places_of_power: Dict[int, bool] = field(default_factory=dict)


@dataclass
class GameState:
    players: List[PlayerState]
    phase: GamePhase = GamePhase.SETUP
    draft_state: Optional[DraftState] = None
    income_state: Optional[IncomePhaseState] = None

    # Shared zones
    available_monuments: List[Card] = field(default_factory=list)
    available_places_of_power: List[Card] = field(default_factory=list)
    available_magic_items: List[Card] = field(default_factory=list)
    available_scrolls: List[Card] = field(default_factory=list)
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
