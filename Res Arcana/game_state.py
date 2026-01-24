from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ResourceType(str, Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    BLACK = "black"
    GOLD = "gold"


class CardTag(str, Enum):
    """Tags that can be on artifacts (can have multiple or none)."""
    DRAGON = "dragon"
    DEMON = "demon"
    ANIMAL = "animal"


class GamePhase(str, Enum):
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


class CardType(str, Enum):
    ARTIFACT = "artifact"
    PLACE_OF_POWER = "place_of_power"
    MONUMENT = "monument"
    MAGIC_ITEM = "magic_item"
    MAGE = "mage"
    SCROLL = "scroll"


class CostType(str, Enum):
    """Types of costs for abilities."""
    TAP = "tap"                        # Tap this card
    TAP_CARD = "tap_card"              # Tap another card
    PAY = "pay"                        # Pay resources from pool
    PAY_VARIABLE = "pay_variable"      # Pay 1+ resources of same type
    REMOVE_FROM_CARD = "remove_from_card"  # Remove resources from this card
    DESTROY_SELF = "destroy_self"      # Destroy this card
    DESTROY_ARTIFACT = "destroy_artifact"  # Destroy an artifact
    DISCARD = "discard"                # Discard a card from hand


class EffectType(str, Enum):
    """Types of effects for abilities."""
    GAIN = "gain"                      # Gain resources to pool
    GAIN_PER_OPPONENT = "gain_per_opponent"  # Gain based on opponent's resources
    GAIN_PER_OPPONENT_COUNT = "gain_per_opponent_count"  # Gain based on opponent's card count
    GAIN_FROM_DESTROYED = "gain_from_destroyed"  # Gain from destroyed card's cost
    GAIN_FROM_DISCARDED = "gain_from_discarded"  # Gain from discarded card's cost
    ADD_TO_CARD = "add_to_card"        # Add resources to a card
    ADD_PAID_TO_CARD = "add_paid_to_card"  # Add paid resource to card
    TAKE_FROM_CARD = "take_from_card"  # Take resources from another card
    ATTACK = "attack"                  # Attack opponents
    DRAW = "draw"                      # Draw cards
    DRAW_DISCARD = "draw_discard"      # Draw then discard
    UNTAP = "untap"                    # Untap a card
    CONVERT = "convert"                # Convert resources to gold
    PLAY_CARD = "play_card"            # Play a card from hand/discard
    GIVE_OPPONENTS = "give_opponents"  # Give resources to opponents
    REORDER_DECK = "reorder_deck"      # Look at/reorder top cards
    IGNORE_ATTACK = "ignore_attack"    # Ignore an attack (reaction)


class TriggerType(str, Enum):
    """Trigger types for reaction abilities."""
    ATTACKED = "attacked"              # When attacked
    ATTACKED_BY_DRAGON = "attacked_by_dragon"  # When attacked by dragon
    ATTACKED_BY_DEMON = "attacked_by_demon"    # When attacked by demon
    ARTIFACT_DESTROYED = "artifact_destroyed"  # When an artifact is destroyed


class PassiveEffectType(str, Enum):
    """Types of passive effects."""
    COST_REDUCTION = "cost_reduction"  # Reduce cost to play cards


@dataclass
class IncomeEffect:
    """Represents income a card can generate each round.

    Two modes:
    1. Fixed income: Use 'resources' dict to specify exact resources gained
       - resources={RED: 1, BLUE: 1} → gain 1 red AND 1 blue

    2. Choice income: Use 'count' and 'types' to specify player choice
       - count=1, types=[BLACK, GREEN] → gain 1 black OR green (player chooses)
       - count=2, types=[RED, BLUE, GREEN] → gain 2 from red/blue/green in any combination

    Other fields:
    - conditional: If True, income only happens if resources were left on card during collection
    - add_to_card: If True, income adds to card instead of player pool
    """
    # For fixed income (gain specific resources)
    resources: Optional[Dict[ResourceType, int]] = None
    # For choice income (player picks from types)
    count: int = 0
    types: Optional[List[ResourceType]] = None
    # Modifiers
    conditional: bool = False  # True for Vault/Windup Man style income
    add_to_card: bool = False  # True if income adds to card (Windup Man), False for player pool


# ============================================================
# Ability System
# ============================================================

@dataclass
class AbilityCost:
    """A single cost component for an ability."""
    cost_type: CostType
    # Additional fields depending on cost_type
    resources: Optional[Dict[ResourceType, int]] = None  # For pay, remove_from_card
    tag: Optional[CardTag] = None  # For tap_card filter
    must_be_different: bool = True  # For destroy_artifact
    # For pay_variable
    min_amount: int = 1  # Minimum amount to pay
    same_type: bool = False  # If True, all resources must be same type
    types: Optional[List[ResourceType]] = None  # Allowed resource types


@dataclass
class AbilityEffect:
    """A single effect of an ability."""
    effect_type: EffectType
    # Common fields
    resources: Optional[Dict[ResourceType, int]] = None
    count: Optional[int] = None
    types: Optional[List[ResourceType]] = None  # For choice effects
    # For effects that reference paid amount
    amount_from_paid: bool = False  # If True, count equals amount paid
    different_from_paid: bool = False  # If True, must choose different type than paid
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
    card_filter: Optional[CardTag] = None  # Filter by card tag
    # Deck fields
    deck: Optional[str] = None  # 'self', 'monuments'
    # Draw/discard fields
    discard_count: Optional[int] = None
    # Gain per opponent fields
    check_resource: Optional[ResourceType] = None  # Resource type to check
    check_tag: Optional[CardTag] = None  # Card tag to count
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
    trigger: Optional[TriggerType] = None
    trigger_filter: Optional[CardTag] = None  # Filter for trigger (e.g., dragon attacks only)


@dataclass
class PassiveEffect:
    """A permanent passive effect on a card."""
    effect_type: PassiveEffectType
    card_filter: Optional[CardTag] = None  # Filter by card tag
    amount: int = 0
    reduction_type: str = 'non_gold'  # 'any' includes gold, 'non_gold' excludes gold


@dataclass
class CardEffects:
    """All effects a card can have."""
    income: Optional[IncomeEffect] = None
    # Cost to play (dict of ResourceType -> count)
    # 'any' key means any non-gold essence
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
