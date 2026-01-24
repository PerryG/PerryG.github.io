from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ResourceType(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    BLACK = "black"
    GOLD = "gold"


class CardTag(Enum):
    """Tags that can be on artifacts (can have multiple or none)."""
    DRAGON = "dragon"
    DEMON = "demon"
    ANIMAL = "animal"


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
    GAME_OVER = "game_over"                  # Game has ended


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
    conditional: If True, income only happens if resources were left on card during collection

    Examples:
    - count=1, types=['green'] → gain 1 green (fixed)
    - count=1, types=['black', 'green'] → gain 1 black OR green
    - count=2, types=['green', 'blue', 'red'] → gain 2 from green/blue/red in any combination
    - count=3, types=['red', 'blue', 'green', 'black'] → gain 3 of any non-gold
    """
    count: int
    types: List[str]
    conditional: bool = False  # True for Vault/Windup Man style income
    add_to_card: bool = False  # True if income adds to card (Windup Man), False for player pool


# ============================================================
# Ability System
# ============================================================

@dataclass
class AbilityCost:
    """A single cost component for an ability.

    Cost types and their expected fields:
    - tap: Tap this card (no additional fields)
    - tap_card: Tap another card. Fields: tag (optional CardTag filter)
    - pay: Pay resources from player pool. Fields: resources (dict)
    - remove_from_card: Remove resources from this card. Fields: resources (dict)
    - destroy_self: Destroy this card (no additional fields)
    - destroy_artifact: Destroy another artifact. Fields: must_be_different (bool)
    - discard: Discard a card from hand (no additional fields)
    """
    cost_type: str
    # Additional fields depending on cost_type
    resources: Optional[Dict[str, int]] = None
    tag: Optional[str] = None  # For tap_card filter
    must_be_different: bool = True  # For destroy_artifact


@dataclass
class AbilityEffect:
    """A single effect of an ability.

    Effect types and their expected fields:
    - gain: Gain resources to player pool. Fields: resources OR count+types (for choice)
    - gain_per_opponent: Gain based on max resource among opponents. Fields: resources (what to gain), check_resource
    - gain_per_opponent_count: Gain based on max card count. Fields: resources, check_tag
    - gain_from_destroyed: Gain from destroyed card's cost. Fields: bonus
    - gain_from_discarded: Gain from discarded card's cost.
    - add_to_card: Add resources to this/another card. Fields: resources OR count+types, target
    - add_paid_to_card: Add the paid resource to the card.
    - take_from_card: Take all resources from another card. Fields: target
    - attack: Attack opponents. Fields: green_cost, avoid_cost (optional dict or special string)
    - draw: Draw cards. Fields: count
    - draw_discard: Draw then discard. Fields: count, discard_count
    - untap: Untap a card. Fields: target (self/other/demon/dragon/etc)
    - convert: Convert resources to gold.
    - exchange: Exchange resources (Prism style). Fields: target
    - play_card: Play a card. Fields: source (hand/discard), discount, free, card_filter
    - give_opponents: Give resources to opponents. Fields: resources
    - reorder_deck: Look at top N cards. Fields: count, deck (self/monuments)
    - ignore_attack: Ignore an attack (for reactions).
    """
    effect_type: str
    # Common fields
    resources: Optional[Dict[str, int]] = None
    count: Optional[int] = None
    types: Optional[List[str]] = None  # For choice effects
    # Attack fields
    green_cost: Optional[int] = None
    avoid_cost: Optional[Dict] = None  # Can be resources, 'discard', 'destroy_artifact', etc.
    # Target fields
    target: Optional[str] = None  # 'self', 'other', 'dragon', 'demon', etc.
    target_card: Optional[str] = None
    # Play card fields
    source: Optional[str] = None  # 'hand', 'discard'
    discount: Optional[int] = None
    discount_type: Optional[str] = None  # 'any' or 'non_gold'
    free: bool = False
    card_filter: Optional[str] = None  # 'dragon', 'demon', etc.
    # Deck fields
    deck: Optional[str] = None  # 'self', 'monuments'
    # Draw/discard fields
    discard_count: Optional[int] = None
    # Gain per opponent fields
    check_resource: Optional[str] = None  # Resource type to check on opponents
    check_tag: Optional[str] = None  # Card tag to count on opponents
    # Gain from destroyed/discarded fields
    bonus: int = 0  # Bonus resources to add to card's cost


@dataclass
class Ability:
    """An activated ability on a card.

    For regular abilities: costs + effects
    For reactions: trigger + costs + effects
    """
    costs: List[AbilityCost] = field(default_factory=list)
    effects: List[AbilityEffect] = field(default_factory=list)
    # For reactions
    trigger: Optional[str] = None  # 'attacked', 'attacked_by_dragon', 'attacked_by_demon', 'artifact_destroyed'
    trigger_filter: Optional[str] = None  # Additional filter for trigger


@dataclass
class PassiveEffect:
    """A permanent passive effect on a card.

    Effect types:
    - cost_reduction: Reduce cost to play certain cards.
      Fields: card_filter, amount, reduction_type ('any' or 'non_gold')
    """
    effect_type: str
    card_filter: Optional[str] = None  # 'dragon', 'demon', etc.
    amount: int = 0
    reduction_type: str = 'non_gold'  # 'any' includes gold, 'non_gold' excludes gold


@dataclass
class CardEffects:
    """All effects a card can have."""
    income: Optional[IncomeEffect] = None
    # Cost to play (dict of resource_type -> count, e.g. {'red': 2, 'black': 1})
    # 'any' means any non-gold essence
    cost: Optional[Dict[str, int]] = None
    # Abilities (tap abilities, reactions)
    abilities: List[Ability] = field(default_factory=list)
    # Passive effects (cost reductions, etc.)
    passives: List[PassiveEffect] = field(default_factory=list)


@dataclass
class Card:
    name: str
    card_type: CardType
    effects: Optional[CardEffects] = None
    # Tags for card classification (Dragon, Demon, Animal)
    tags: Set[str] = field(default_factory=set)
    # Victory points this card is worth
    points: int = 0


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
    # Cards waiting to be passed to next player (after picking)
    cards_to_pass: Dict[int, List[Card]] = field(default_factory=dict)
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
class ActionPhaseState:
    """Tracks state during the action (playing) phase."""
    # Current player whose turn it is
    current_player: int = 0
    # Which players have passed this round
    passed: Dict[int, bool] = field(default_factory=dict)


@dataclass
class GameState:
    players: List[PlayerState]
    phase: GamePhase = GamePhase.SETUP
    draft_state: Optional[DraftState] = None
    income_state: Optional[IncomePhaseState] = None
    action_state: Optional[ActionPhaseState] = None

    # Shared zones
    available_monuments: List[Card] = field(default_factory=list)
    available_places_of_power: List[Card] = field(default_factory=list)
    available_magic_items: List[Card] = field(default_factory=list)
    available_scrolls: List[Card] = field(default_factory=list)
    monument_deck: List[Card] = field(default_factory=list)

    # Victory state (set when game ends)
    victory_result: Optional[Dict] = None

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
