// Renderer for Res Arcana game state

// Resource type constants (must match Python ResourceType enum)
const ResourceType = {
    RED: 'red',
    BLUE: 'blue',
    GREEN: 'green',
    BLACK: 'black',
    GOLD: 'gold'
};

// Game phase constants (must match Python GamePhase enum)
const GamePhase = {
    SETUP: 'setup',
    DRAFTING_ROUND_1: 'drafting_round_1',
    DRAFTING_ROUND_2: 'drafting_round_2',
    MAGE_SELECTION: 'mage_selection',
    MAGIC_ITEM_SELECTION: 'magic_item_selection',
    INCOME: 'income',
    PLAYING: 'playing',
    GAME_OVER: 'game_over'
};

// Current game state and viewing player (for interaction handlers)
let currentGameState = null;
let currentViewingPlayer = 0;

// ============================================================
// API Functions
// ============================================================

async function apiNewGame(numPlayers = 2, humanPlayerId = 0) {
    const response = await fetch('/api/new-game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ numPlayers, humanPlayerId })
    });
    return response.json();
}

async function apiGetState(playerId) {
    const response = await fetch(`/api/state?playerId=${playerId}`);
    if (response.status === 404) return null;
    return response.json();
}

async function apiGetFullState() {
    const response = await fetch('/api/state/full');
    if (response.status === 404 || response.status === 403) return null;
    return response.json();
}

async function apiDraftPick(playerId, cardName) {
    const response = await fetch('/api/draft/pick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId, cardName })
    });
    return response.json();
}

async function apiMageSelect(playerId, mageName) {
    const response = await fetch('/api/mage/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId, mageName })
    });
    return response.json();
}

async function apiMagicItemSelect(playerId, itemName) {
    const response = await fetch('/api/magic-item/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId, itemName })
    });
    return response.json();
}

// Income phase API functions
async function apiIncomeStart(playerId) {
    const response = await fetch('/api/income/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId })
    });
    return response.json();
}

async function apiIncomeCollectionChoice(playerId, cardName, takeAll) {
    const response = await fetch('/api/income/collection-choice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId, cardName, takeAll })
    });
    return response.json();
}

async function apiIncomeIncomeChoice(playerId, cardName, resources) {
    const response = await fetch('/api/income/income-choice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId, cardName, resources })
    });
    return response.json();
}

async function apiIncomeToggleAutoSkipPoP(playerId, autoSkip) {
    const response = await fetch('/api/income/toggle-auto-skip-pop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId, autoSkip })
    });
    return response.json();
}

async function apiIncomeWait(playerId) {
    const response = await fetch('/api/income/wait', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId })
    });
    return response.json();
}

async function apiIncomeFinalize(playerId) {
    const response = await fetch('/api/income/finalize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId })
    });
    return response.json();
}

// Action phase API functions
async function apiActionPass(playerId, newMagicItem = null) {
    const body = { playerId };
    if (newMagicItem) body.newMagicItem = newMagicItem;
    const response = await fetch('/api/action/pass', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return response.json();
}

async function apiActionPlayCard(playerId, cardName, anyPayment = null) {
    const body = { playerId, cardName };
    if (anyPayment) body.anyPayment = anyPayment;
    const response = await fetch('/api/action/play-card', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return response.json();
}

async function apiActionBuyPlaceOfPower(playerId, popName) {
    const response = await fetch('/api/action/buy-place-of-power', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId, popName })
    });
    return response.json();
}

async function apiActionBuyMonument(playerId, monumentName = null, fromDeck = false) {
    const body = { playerId, fromDeck };
    if (monumentName) body.monumentName = monumentName;
    const response = await fetch('/api/action/buy-monument', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return response.json();
}

async function apiActionDiscardCard(playerId, cardName, gainGold = false, gainResources = null) {
    const body = { playerId, cardName };
    if (gainGold) body.gainGold = true;
    if (gainResources) body.gainResources = gainResources;
    const response = await fetch('/api/action/discard-card', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return response.json();
}

async function apiGetAbilities(playerId) {
    const response = await fetch(`/api/action/get-abilities?playerId=${playerId}`);
    return response.json();
}

async function apiUseAbility(playerId, cardName, abilityIndex, costChoices = {}, effectChoices = {}) {
    const response = await fetch('/api/action/use-ability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId, cardName, abilityIndex, costChoices, effectChoices })
    });
    return response.json();
}

async function startNewGame(numPlayers = 2, humanPlayerId = 0) {
    const state = await apiNewGame(numPlayers, humanPlayerId);
    if (state.error) {
        console.error('Error starting game:', state.error);
        return;
    }
    currentGameState = state;
    currentViewingPlayer = humanPlayerId;
    renderGame(state, currentViewingPlayer);
}

async function loadCurrentGame() {
    const state = await apiGetState(currentViewingPlayer);
    if (state && !state.error) {
        currentGameState = state;
        renderGame(state, currentViewingPlayer);
        return true;
    }
    return false;
}

/**
 * Filter game state to only show what's visible to a specific player.
 * Hidden information:
 * - Other players' hands (show count only)
 * - Contents of any player's deck (show count only)
 * - Contents of monument deck (show count only)
 */
function getVisibleState(gameState, viewingPlayerId) {
    const visibleState = {
        players: gameState.players.map(player => {
            const isViewingPlayer = player.playerId === viewingPlayerId;
            return {
                playerId: player.playerId,
                mage: player.mage,
                magicItem: player.magicItem,
                artifacts: player.artifacts,
                monuments: player.monuments,
                placesOfPower: player.placesOfPower,
                scrolls: player.scrolls,
                // Hand: visible only to owning player
                hand: isViewingPlayer ? player.hand : null,
                handCount: player.hand.length,
                // Deck: only count visible
                deckCount: player.deck.length,
                // Discard: visible to all
                discard: player.discard,
                resources: player.resources,
                hasFirstPlayerToken: player.hasFirstPlayerToken,
                firstPlayerTokenFaceUp: player.firstPlayerTokenFaceUp
            };
        }),
        availableMonuments: gameState.availableMonuments,
        availablePlacesOfPower: gameState.availablePlacesOfPower,
        availableMagicItems: gameState.availableMagicItems,
        availableScrolls: gameState.availableScrolls,
        monumentDeckCount: gameState.monumentDeck.length
    };
    return visibleState;
}

/**
 * Create HTML for a resource icon
 */
function renderResourceIcon(resourceType) {
    return `<span class="resource-icon ${resourceType}"></span>`;
}

/**
 * Create HTML for a player's unplaced resources
 */
function renderPlayerResources(resources) {
    const types = [ResourceType.RED, ResourceType.BLUE, ResourceType.GREEN, ResourceType.BLACK, ResourceType.GOLD];
    return types.map(type => {
        const count = resources[type] || 0;
        return `<div class="resource">${renderResourceIcon(type)}<span>${count}</span></div>`;
    }).join('');
}

/**
 * Create HTML for resources on a card
 */
function renderCardResources(resources) {
    if (!resources || Object.keys(resources).length === 0) return '';

    let html = '';
    for (const [type, count] of Object.entries(resources)) {
        for (let i = 0; i < count; i++) {
            html += renderResourceIcon(type);
        }
    }
    return `<div class="card-resources">${html}</div>`;
}

// All magic item names in fixed order
const ALL_MAGIC_ITEMS = [
    "Alchemy", "Calm | Elan", "Death | Life", "Divination", "Protection",
    "Reanimate", "Research", "Transmutation", "Illusion", "Inscription"
];

// All scroll names in fixed order
const ALL_SCROLLS = [
    "Augury", "Destruction", "Disjunction", "Projection",
    "Revivify", "Shield", "Transform", "Vitality"
];

/**
 * Render fixed slots for items that shouldn't shift when taken
 */
function renderFixedSlots(availableItems, allItemNames) {
    let html = '';
    for (const name of allItemNames) {
        const item = availableItems.find(c => c.name === name);
        if (item) {
            html += renderCard(item);
        } else {
            html += '<div class="card-slot empty"></div>';
        }
    }
    return html;
}

/**
 * Format an ability cost for display
 */
function formatAbilityCost(cost) {
    switch (cost.costType) {
        case 'tap':
            return 'Tap';
        case 'tap_card':
            return cost.tag ? `Tap ${cost.tag}` : 'Tap card';
        case 'pay':
            if (cost.resources) {
                return Object.entries(cost.resources)
                    .map(([type, count]) => `${count}${type[0].toUpperCase()}`)
                    .join('');
            }
            return 'Pay';
        case 'remove_from_card':
            if (cost.resources) {
                return Object.entries(cost.resources)
                    .map(([type, count]) => `-${count}${type[0].toUpperCase()}`)
                    .join('');
            }
            return 'Remove';
        case 'destroy_self':
            return 'Destroy self';
        case 'destroy_artifact':
            return 'Destroy artifact';
        case 'discard':
            return 'Discard';
        default:
            return cost.costType;
    }
}

/**
 * Format an ability effect for display
 */
function formatAbilityEffect(effect) {
    switch (effect.effectType) {
        case 'gain':
            if (effect.resources) {
                return '+' + Object.entries(effect.resources)
                    .map(([type, count]) => `${count}${type[0].toUpperCase()}`)
                    .join('');
            }
            if (effect.count && effect.types) {
                return `+${effect.count} ${effect.types.join('/')}`;
            }
            return 'Gain';
        case 'add_to_card':
            if (effect.resources) {
                return 'Store ' + Object.entries(effect.resources)
                    .map(([type, count]) => `${count}${type[0].toUpperCase()}`)
                    .join('');
            }
            return 'Add to card';
        case 'attack':
            return `Attack ${effect.greenCost}G`;
        case 'draw':
            return `Draw ${effect.count || 1}`;
        case 'untap':
            return effect.target === 'self' ? 'Untap' : `Untap ${effect.target}`;
        case 'convert':
            return 'Convert to gold';
        case 'give_opponents':
            return 'Give opponents';
        default:
            return effect.effectType;
    }
}

/**
 * Create HTML for ability buttons on a card
 */
function renderAbilityButtons(card, cardName, isMyTurn, isTapped) {
    if (!card.effects?.abilities) return '';

    const abilities = card.effects.abilities.filter(a => !a.trigger); // Only show activated abilities, not reactions
    if (abilities.length === 0) return '';

    return `<div class="ability-buttons">${abilities.map((ability, index) => {
        const costs = ability.costs.map(formatAbilityCost).join(', ');
        const effects = ability.effects.map(formatAbilityEffect).join(', ');
        const disabled = !isMyTurn || isTapped;
        const disabledClass = disabled ? 'disabled' : '';

        return `
            <button class="ability-btn ${disabledClass}"
                    onclick="event.stopPropagation(); useAbility('${cardName}', ${index})"
                    ${disabled ? 'disabled' : ''}
                    title="${costs} → ${effects}">
                ${effects}
            </button>
        `;
    }).join('')}</div>`;
}

/**
 * Create HTML for a single card
 */
function renderCard(card, controlled = null, showAbilities = false, isMyTurn = false) {
    const tappedClass = controlled?.tapped ? 'tapped' : '';
    const typeClass = card.cardType;
    const resourcesHtml = controlled ? renderCardResources(controlled.resources) : '';

    // Show tags and points if present
    let tagsHtml = '';
    if (card.tags && card.tags.length > 0) {
        tagsHtml = `<div class="card-tags">${card.tags.map(t => `<span class="tag tag-${t}">${t}</span>`).join('')}</div>`;
    }

    let pointsHtml = '';
    if (card.points) {
        pointsHtml = `<div class="card-points">${card.points} VP</div>`;
    }

    // Show abilities if enabled
    const abilitiesHtml = showAbilities ? renderAbilityButtons(card, card.name, isMyTurn, controlled?.tapped) : '';

    return `
        <div class="card ${typeClass} ${tappedClass}">
            <div class="card-name">${card.name}</div>
            ${tagsHtml}
            ${pointsHtml}
            ${resourcesHtml}
            ${abilitiesHtml}
        </div>
    `;
}

/**
 * Create HTML for a controlled card (card on table with state)
 */
function renderControlledCard(controlledCard, showAbilities = false, isMyTurn = false) {
    return renderCard(controlledCard.card, controlledCard, showAbilities, isMyTurn);
}

/**
 * Render all controlled cards for a player
 */
function renderControlledCards(player, showAbilities = false, isMyTurn = false) {
    let html = '';

    // Mage and Magic Item first (skip if empty/placeholder)
    if (player.mage?.card?.name) {
        html += renderControlledCard(player.mage, showAbilities, isMyTurn);
    }
    if (player.magicItem?.card?.name) {
        html += renderControlledCard(player.magicItem, showAbilities, isMyTurn);
    }

    // Then artifacts
    for (const artifact of player.artifacts) {
        html += renderControlledCard(artifact, showAbilities, isMyTurn);
    }

    // Then places of power
    for (const pop of player.placesOfPower) {
        html += renderControlledCard(pop, showAbilities, isMyTurn);
    }

    // Then monuments
    for (const monument of player.monuments) {
        html += renderControlledCard(monument, showAbilities, isMyTurn);
    }

    return html;
}

/**
 * Render the first player token indicator
 */
function renderFirstPlayerToken(player) {
    if (!player.hasFirstPlayerToken) return '';
    const faceDownClass = player.firstPlayerTokenFaceUp ? '' : 'face-down';
    return `<div class="first-player-token ${faceDownClass}">1st</div>`;
}

/**
 * Generate HTML for an opponent area
 */
function renderOpponentArea(opponent, index) {
    const playerNum = opponent.playerId + 1;  // 1-indexed for display
    const points = opponent.points || 0;
    const label = `Player ${playerNum} - ${points} VP`;
    return `
        <div class="player-area opponent-area" id="opponent-area-${index}">
            <div class="area-label">${label}</div>
            <div class="player-info-bar">
                <div class="player-resources">${renderPlayerResources(opponent.resources)}</div>
                <div class="first-player-slot">${renderFirstPlayerToken(opponent)}</div>
            </div>
            <div class="player-board">
                <div class="side-piles">
                    <div class="discard-area">
                        <div class="zone-label">Discard</div>
                        <div class="discard-cards">${opponent.discard.map(card => renderCard(card)).join('')}</div>
                    </div>
                    <div class="deck">
                        <span class="deck-label">Deck</span>
                        <span class="deck-count">${opponent.deckCount}</span>
                    </div>
                    <div class="deck hidden-hand">
                        <span class="deck-label">Hand</span>
                        <span class="deck-count">${opponent.handCount}</span>
                    </div>
                </div>
                <div class="controlled-cards">${renderControlledCards(opponent)}</div>
                <div class="player-scrolls">${opponent.scrolls.map(card => renderCard(card)).join('')}</div>
            </div>
        </div>
    `;
}

// ============================================================
// Draft Phase Rendering
// ============================================================

/**
 * Create HTML for a selectable card during drafting
 */
function renderSelectableCard(card, onClickHandler) {
    const typeClass = card.cardType;
    return `
        <div class="card ${typeClass} selectable" onclick="${onClickHandler}">
            <div class="card-name">${card.name}</div>
        </div>
    `;
}

/**
 * Render the draft section based on current game phase
 */
function renderDraftSection(gameState, viewingPlayerId) {
    const section = document.getElementById('draft-section');
    const phase = gameState.phase;
    const draftState = gameState.draftState;

    // Only show during draft-related phases
    const draftPhases = [
        GamePhase.SETUP,
        GamePhase.DRAFTING_ROUND_1,
        GamePhase.DRAFTING_ROUND_2,
        GamePhase.MAGE_SELECTION,
        GamePhase.MAGIC_ITEM_SELECTION
    ];

    if (!draftPhases.includes(phase)) {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');

    // Hide all sub-sections initially
    document.getElementById('draft-cards').classList.add('hidden');
    document.getElementById('mage-selection').classList.add('hidden');
    document.getElementById('magic-item-selection').classList.add('hidden');
    document.getElementById('waiting-indicator').classList.add('hidden');
    document.getElementById('your-mages').classList.add('hidden');

    const titleEl = document.getElementById('draft-title');
    const instructionsEl = document.getElementById('draft-instructions');

    if (phase === GamePhase.DRAFTING_ROUND_1 || phase === GamePhase.DRAFTING_ROUND_2) {
        renderDraftPhase(gameState, viewingPlayerId);
    } else if (phase === GamePhase.MAGE_SELECTION) {
        renderMageSelectionPhase(gameState, viewingPlayerId);
    } else if (phase === GamePhase.MAGIC_ITEM_SELECTION) {
        renderMagicItemSelectionPhase(gameState, viewingPlayerId);
    } else if (phase === GamePhase.SETUP) {
        titleEl.textContent = 'Setting up game...';
        instructionsEl.textContent = 'Dealing cards to players.';
    }
}

/**
 * Render the card drafting phase
 */
function renderDraftPhase(gameState, viewingPlayerId) {
    const draftState = gameState.draftState;
    const phase = gameState.phase;

    const titleEl = document.getElementById('draft-title');
    const instructionsEl = document.getElementById('draft-instructions');
    const draftCardsSection = document.getElementById('draft-cards');
    const optionsEl = document.getElementById('draft-card-options');

    const roundNum = phase === GamePhase.DRAFTING_ROUND_1 ? 1 : 2;
    const direction = roundNum === 1 ? 'clockwise' : 'counter-clockwise';
    titleEl.textContent = `Draft Round ${roundNum}`;
    instructionsEl.textContent = `Pick one card, pass the rest ${direction}.`;

    // Get cards available to this player
    const cardsToPickObj = draftState.cardsToPick || {};
    const cardsToPick = cardsToPickObj[viewingPlayerId] || [];

    if (cardsToPick.length > 0) {
        draftCardsSection.classList.remove('hidden');
        optionsEl.innerHTML = cardsToPick.map((card, idx) =>
            renderSelectableCard(card, `selectDraftCard(${idx})`)
        ).join('');
    } else {
        document.getElementById('waiting-indicator').classList.remove('hidden');
    }

    // Show drafted cards
    const draftedCardsObj = draftState.draftedCards || {};
    const draftedCards = draftedCardsObj[viewingPlayerId] || [];
    document.getElementById('drafted-cards').innerHTML =
        draftedCards.map(card => renderCard(card)).join('');

    // Show mage options during drafting (for reference)
    const mageOptionsObj = draftState.mageOptions || {};
    const mageOptions = mageOptionsObj[viewingPlayerId] || [];
    if (mageOptions.length > 0) {
        document.getElementById('your-mages').classList.remove('hidden');
        document.getElementById('your-mage-cards').innerHTML =
            mageOptions.map(mage => renderCard(mage)).join('');
    }
}

/**
 * Render the mage selection phase
 */
function renderMageSelectionPhase(gameState, viewingPlayerId) {
    const draftState = gameState.draftState;

    const titleEl = document.getElementById('draft-title');
    const instructionsEl = document.getElementById('draft-instructions');
    const mageSection = document.getElementById('mage-selection');
    const optionsEl = document.getElementById('mage-options');

    titleEl.textContent = 'Choose Your Mage';

    const mageOptionsObj = draftState.mageOptions || {};
    const mageOptions = mageOptionsObj[viewingPlayerId] || [];
    const selectedMage = draftState.selectedMage?.[viewingPlayerId];

    if (!selectedMage && mageOptions.length > 0) {
        instructionsEl.textContent = 'Select one of your two mages. All mages will be revealed simultaneously.';
        mageSection.classList.remove('hidden');
        optionsEl.innerHTML = mageOptions.map((mage, idx) =>
            renderSelectableCard(mage, `selectMage(${idx})`)
        ).join('');
    } else if (selectedMage) {
        instructionsEl.textContent = 'Waiting for other players to select their mages...';
        document.getElementById('waiting-indicator').classList.remove('hidden');
    }

    // Show drafted cards (and selected mage if chosen)
    const draftedCardsObj = draftState.draftedCards || {};
    const draftedCards = draftedCardsObj[viewingPlayerId] || [];

    let draftedHtml = '';
    if (selectedMage) {
        draftedHtml += `<div class="selected-mage-wrapper">${renderCard(selectedMage)}</div>`;
    }
    draftedHtml += draftedCards.map(card => renderCard(card)).join('');
    document.getElementById('drafted-cards').innerHTML = draftedHtml;
}

/**
 * Render the magic item selection phase
 */
function renderMagicItemSelectionPhase(gameState, viewingPlayerId) {
    const draftState = gameState.draftState;

    const titleEl = document.getElementById('draft-title');
    const instructionsEl = document.getElementById('draft-instructions');
    const itemSection = document.getElementById('magic-item-selection');
    const optionsEl = document.getElementById('magic-item-options');

    titleEl.textContent = 'Choose Magic Item';

    const currentSelector = draftState.magicItemSelector;
    const isMyTurn = currentSelector === viewingPlayerId;

    if (isMyTurn) {
        instructionsEl.textContent = 'Your turn! Choose a magic item.';
        itemSection.classList.remove('hidden');
        optionsEl.innerHTML = gameState.availableMagicItems.map((item, idx) =>
            renderSelectableCard(item, `selectMagicItem(${idx})`)
        ).join('');
    } else {
        instructionsEl.textContent = `Waiting for Player ${currentSelector + 1} to choose...`;
        document.getElementById('waiting-indicator').classList.remove('hidden');
    }

    // Show drafted cards and selected mage
    const draftedCardsObj = draftState.draftedCards || {};
    const draftedCards = draftedCardsObj[viewingPlayerId] || [];
    const selectedMage = draftState.selectedMage?.[viewingPlayerId];

    let draftedHtml = '';
    if (selectedMage) {
        draftedHtml += `<div class="selected-mage-wrapper">${renderCard(selectedMage)}</div>`;
    }
    draftedHtml += draftedCards.map(card => renderCard(card)).join('');
    document.getElementById('drafted-cards').innerHTML = draftedHtml;
}

// ============================================================
// Draft Interaction Handlers
// ============================================================

/**
 * Called when player clicks a card during drafting
 */
async function selectDraftCard(cardIndex) {
    if (!currentGameState || !currentGameState.draftState) return;

    const cardsToPick = currentGameState.draftState.cardsToPick[currentViewingPlayer];
    if (!cardsToPick || cardIndex >= cardsToPick.length) return;

    const selectedCard = cardsToPick[cardIndex];
    console.log('Selected draft card:', selectedCard.name);

    const state = await apiDraftPick(currentViewingPlayer, selectedCard.name);
    if (state.error) {
        console.error('Error picking card:', state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Called when player clicks a mage during mage selection
 */
async function selectMage(mageIndex) {
    if (!currentGameState || !currentGameState.draftState) return;

    const mageOptions = currentGameState.draftState.mageOptions[currentViewingPlayer];
    if (!mageOptions || mageIndex >= mageOptions.length) return;

    const selectedMage = mageOptions[mageIndex];
    console.log('Selected mage:', selectedMage.name);

    const state = await apiMageSelect(currentViewingPlayer, selectedMage.name);
    if (state.error) {
        console.error('Error selecting mage:', state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Called when player clicks a magic item during magic item selection
 */
async function selectMagicItem(itemIndex) {
    if (!currentGameState) return;

    const items = currentGameState.availableMagicItems;
    if (!items || itemIndex >= items.length) return;

    const selectedItem = items[itemIndex];
    console.log('Selected magic item:', selectedItem.name);

    const state = await apiMagicItemSelect(currentViewingPlayer, selectedItem.name);
    if (state.error) {
        console.error('Error selecting magic item:', state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

// ============================================================
// Income Phase Rendering
// ============================================================

/**
 * Render the income section based on current game phase
 */
function renderIncomeSection(gameState, viewingPlayerId) {
    const section = document.getElementById('income-section');
    if (!section) return;

    // Hide section if not in income phase
    if (gameState.phase !== GamePhase.INCOME) {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');

    const incomeState = gameState.incomeState;
    if (!incomeState) return;

    const playerInfo = incomeState.cardsInfo?.[viewingPlayerId] || {};
    const isFinalized = incomeState.finalized?.[viewingPlayerId] || false;
    const isWaiting = incomeState.waitingForEarlier?.[viewingPlayerId] || false;
    const collectionChoices = incomeState.collectionChoices?.[viewingPlayerId] || {};
    const incomeChoices = incomeState.incomeChoices?.[viewingPlayerId] || {};
    const autoSkipPoP = incomeState.autoSkipPlacesOfPower?.[viewingPlayerId] ?? true;

    // Check if player is first player (can't wait)
    const isFirstPlayer = gameState.players.find(p => p.playerId === viewingPlayerId)?.hasFirstPlayerToken;

    // Title and instructions
    const titleEl = document.getElementById('income-title');
    const instructionsEl = document.getElementById('income-instructions');
    titleEl.textContent = 'Income Phase';

    if (isFinalized) {
        instructionsEl.textContent = 'You have finalized. Waiting for other players...';
    } else if (isWaiting) {
        instructionsEl.textContent = 'Waiting for earlier players to finalize...';
    } else {
        instructionsEl.textContent = 'Collect resources from cards and choose income options.';
    }

    // Render cards with stored resources
    const collectionDiv = document.getElementById('income-collection-cards');
    const cardsWithResources = playerInfo.cardsWithResources || [];
    if (cardsWithResources.length > 0) {
        document.getElementById('income-collection').classList.remove('hidden');
        collectionDiv.innerHTML = cardsWithResources.map(card => {
            const willTake = collectionChoices[card.cardName] || false;
            const isPoP = card.cardType === 'place_of_power';
            const resourcesStr = Object.entries(card.resources)
                .map(([type, count]) => `${count} ${type}`)
                .join(', ');
            return `
                <div class="income-card-choice ${willTake ? 'selected' : ''} ${isFinalized ? 'disabled' : ''}"
                     onclick="${isFinalized ? '' : `toggleCollectionChoice('${card.cardName}')`}">
                    <div class="card-name">${card.cardName}</div>
                    <div class="card-resources-text">${resourcesStr}</div>
                    <div class="choice-status">${willTake ? 'TAKE' : 'LEAVE'}${isPoP && autoSkipPoP ? ' (auto-skip PoP)' : ''}</div>
                </div>
            `;
        }).join('');
    } else {
        document.getElementById('income-collection').classList.add('hidden');
    }

    // Render cards with fixed income (informational)
    const fixedIncomeDiv = document.getElementById('income-fixed-cards');
    const fixedIncomeCards = playerInfo.cardsWithFixedIncome || [];
    if (fixedIncomeCards.length > 0) {
        document.getElementById('income-fixed').classList.remove('hidden');
        fixedIncomeDiv.innerHTML = fixedIncomeCards.map(card => {
            return `
                <div class="income-card-info">
                    <div class="card-name">${card.cardName}</div>
                    <div class="income-gain">+${card.count} ${card.type}</div>
                </div>
            `;
        }).join('');
    } else {
        document.getElementById('income-fixed').classList.add('hidden');
    }

    // Render cards needing income choice
    const choicesDiv = document.getElementById('income-choice-cards');
    const cardsNeedingChoice = playerInfo.cardsNeedingChoice || [];
    if (cardsNeedingChoice.length > 0) {
        document.getElementById('income-choices').classList.remove('hidden');
        choicesDiv.innerHTML = cardsNeedingChoice.map(card => {
            const currentChoice = incomeChoices[card.cardName];
            let optionsHtml = '';

            if (card.count === 1) {
                // Simple choice: pick one type
                optionsHtml = card.types.map(type => {
                    const opt = { [type]: 1 };
                    const isSelected = JSON.stringify(currentChoice) === JSON.stringify(opt);
                    return `
                        <button class="income-option ${isSelected ? 'selected' : ''}"
                                onclick="selectIncomeOption('${card.cardName}', '${type}', 1)"
                                ${isFinalized ? 'disabled' : ''}>
                            1 ${type}
                        </button>
                    `;
                }).join(' ');
            } else {
                // Multi-resource choice: pick count resources from types
                // For simplicity, show single-type options (e.g., "2 red", "2 blue")
                // TODO: Add UI for mixed allocations (e.g., "1 red + 1 blue")
                optionsHtml = card.types.map(type => {
                    const opt = { [type]: card.count };
                    const isSelected = JSON.stringify(currentChoice) === JSON.stringify(opt);
                    return `
                        <button class="income-option ${isSelected ? 'selected' : ''}"
                                onclick="selectIncomeOption('${card.cardName}', '${type}', ${card.count})"
                                ${isFinalized ? 'disabled' : ''}>
                            ${card.count} ${type}
                        </button>
                    `;
                }).join(' ');
            }

            return `
                <div class="income-card-choice">
                    <div class="card-name">${card.cardName}</div>
                    <div class="income-options">${optionsHtml}</div>
                </div>
            `;
        }).join('');
    } else {
        document.getElementById('income-choices').classList.add('hidden');
    }

    // Update auto-skip checkbox
    const autoSkipCheckbox = document.getElementById('auto-skip-pop');
    if (autoSkipCheckbox) {
        autoSkipCheckbox.checked = autoSkipPoP;
        autoSkipCheckbox.disabled = isFinalized;
    }

    // Update action buttons
    const waitBtn = document.getElementById('income-wait-btn');
    const finalizeBtn = document.getElementById('income-finalize-btn');

    if (waitBtn) {
        waitBtn.disabled = isFinalized || isWaiting || isFirstPlayer;
        if (isFirstPlayer) {
            waitBtn.title = 'First player cannot wait';
        }
    }

    if (finalizeBtn) {
        // Check if can finalize (not waiting for others)
        let canFinalize = !isFinalized;
        if (isWaiting) {
            // Check if all earlier players have finalized
            const turnOrder = getTurnOrder(gameState);
            for (const pid of turnOrder) {
                if (pid === viewingPlayerId) break;
                if (!incomeState.finalized?.[pid]) {
                    canFinalize = false;
                    break;
                }
            }
        }
        finalizeBtn.disabled = !canFinalize;
    }

    // Show finalization status
    const statusDiv = document.getElementById('income-status');
    if (statusDiv) {
        const statusHtml = gameState.players.map(p => {
            const finalized = incomeState.finalized?.[p.playerId];
            const waiting = incomeState.waitingForEarlier?.[p.playerId];
            let status = finalized ? 'Done' : (waiting ? 'Waiting...' : 'Choosing...');
            return `<span class="player-status ${finalized ? 'done' : ''}">P${p.playerId + 1}: ${status}</span>`;
        }).join(' | ');
        statusDiv.innerHTML = statusHtml;
    }
}

/**
 * Get turn order starting from first player
 */
function getTurnOrder(gameState) {
    const firstPlayerId = gameState.players.find(p => p.hasFirstPlayerToken)?.playerId || 0;
    const numPlayers = gameState.players.length;
    const order = [];
    for (let i = 0; i < numPlayers; i++) {
        order.push((firstPlayerId + i) % numPlayers);
    }
    return order;
}

// ============================================================
// Income Interaction Handlers
// ============================================================

/**
 * Toggle collection choice for a card
 */
async function toggleCollectionChoice(cardName) {
    if (!currentGameState || !currentGameState.incomeState) return;

    const current = currentGameState.incomeState.collectionChoices?.[currentViewingPlayer]?.[cardName] || false;
    const state = await apiIncomeCollectionChoice(currentViewingPlayer, cardName, !current);

    if (state.error) {
        console.error('Error setting collection choice:', state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Select income option for a card
 */
async function selectIncomeOption(cardName, type, count) {
    if (!currentGameState || !currentGameState.incomeState) return;

    const resources = { [type]: count };
    const state = await apiIncomeIncomeChoice(currentViewingPlayer, cardName, resources);

    if (state.error) {
        console.error('Error setting income choice:', state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Toggle auto-skip Places of Power preference
 */
async function toggleAutoSkipPoP() {
    if (!currentGameState || !currentGameState.incomeState) return;

    const current = currentGameState.incomeState.autoSkipPlacesOfPower?.[currentViewingPlayer] ?? true;
    const state = await apiIncomeToggleAutoSkipPoP(currentViewingPlayer, !current);

    if (state.error) {
        console.error('Error toggling auto-skip:', state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Wait for earlier players to finalize
 */
async function waitForEarlierPlayers() {
    if (!currentGameState) return;

    const state = await apiIncomeWait(currentViewingPlayer);

    if (state.error) {
        console.error('Error waiting:', state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Finalize income choices
 */
async function finalizeIncome() {
    if (!currentGameState) return;

    const state = await apiIncomeFinalize(currentViewingPlayer);

    if (state.error) {
        console.error('Error finalizing:', state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Start the income phase (for testing)
 */
async function startIncomePhase() {
    if (!currentGameState) return;

    const state = await apiIncomeStart(currentViewingPlayer);

    if (state.error) {
        console.error('Error starting income phase:', state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

// ============================================================
// Action Phase Rendering
// ============================================================

/**
 * Render the action section based on current game phase
 */
function renderActionSection(gameState, viewingPlayerId) {
    const section = document.getElementById('action-section');
    if (!section) return;

    // Hide section if not in playing phase
    if (gameState.phase !== GamePhase.PLAYING || !gameState.actionState) {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');

    const actionState = gameState.actionState;
    const currentPlayer = actionState.currentPlayer;
    const isMyTurn = currentPlayer === viewingPlayerId;
    const hasPassed = actionState.passed?.[viewingPlayerId] || false;

    // Title and turn indicator
    const titleEl = document.getElementById('action-title');
    const instructionsEl = document.getElementById('action-instructions');

    titleEl.textContent = 'Action Phase';
    if (hasPassed) {
        instructionsEl.textContent = 'You have passed. Waiting for round to end...';
    } else if (isMyTurn) {
        instructionsEl.textContent = 'Your turn! Play a card, use an ability, buy something, or pass.';
    } else {
        instructionsEl.textContent = `Waiting for Player ${currentPlayer + 1} to take their turn...`;
    }

    // Pass button
    const passBtn = document.getElementById('action-pass-btn');
    if (passBtn) {
        passBtn.disabled = !isMyTurn || hasPassed;
    }

    // Show player status
    const statusDiv = document.getElementById('action-status');
    if (statusDiv) {
        const statusHtml = gameState.players.map(p => {
            const passed = actionState.passed?.[p.playerId];
            const isCurrent = p.playerId === currentPlayer;
            let status = passed ? 'Passed' : (isCurrent ? 'Acting...' : 'Waiting');
            return `<span class="player-status ${passed ? 'passed' : ''} ${isCurrent ? 'current' : ''}">P${p.playerId + 1}: ${status}</span>`;
        }).join(' | ');
        statusDiv.innerHTML = statusHtml;
    }
}

// ============================================================
// Action Interaction Handlers
// ============================================================

/**
 * Use an ability on a card
 */
async function useAbility(cardName, abilityIndex) {
    if (!currentGameState) return;

    console.log(`Using ability ${abilityIndex} on ${cardName}`);

    const state = await apiUseAbility(currentViewingPlayer, cardName, abilityIndex);

    if (state.error) {
        console.error('Error using ability:', state.error);
        alert('Cannot use ability: ' + state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Pass for the rest of the round - requires choosing a new magic item
 */
async function passAction() {
    if (!currentGameState) return;

    // Show magic item selection dialog
    const availableMagicItems = currentGameState.availableMagicItems || [];
    if (availableMagicItems.length === 0) {
        alert('No magic items available to swap!');
        return;
    }

    // For now, use a simple prompt. TODO: Make a nicer UI for this
    const options = availableMagicItems.map((item, i) => `${i + 1}. ${item.name}`).join('\n');
    const choice = prompt(
        `Choose a new magic item (you'll return your current one):\n\n${options}\n\nEnter number (1-${availableMagicItems.length}):`
    );

    if (choice === null) return; // Cancelled

    const index = parseInt(choice) - 1;
    if (isNaN(index) || index < 0 || index >= availableMagicItems.length) {
        alert('Invalid selection');
        return;
    }

    const newMagicItem = availableMagicItems[index].name;
    const state = await apiActionPass(currentViewingPlayer, newMagicItem);

    if (state.error) {
        console.error('Error passing:', state.error);
        alert('Cannot pass: ' + state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Play a card from hand
 */
async function playCard(cardName) {
    if (!currentGameState) return;

    const state = await apiActionPlayCard(currentViewingPlayer, cardName);

    if (state.error) {
        console.error('Error playing card:', state.error);
        alert('Cannot play card: ' + state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Buy a Place of Power
 */
async function buyPlaceOfPower(popName) {
    if (!currentGameState) return;

    const state = await apiActionBuyPlaceOfPower(currentViewingPlayer, popName);

    if (state.error) {
        console.error('Error buying Place of Power:', state.error);
        alert('Cannot buy: ' + state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Buy a Monument
 */
async function buyMonument(monumentName = null, fromDeck = false) {
    if (!currentGameState) return;

    const state = await apiActionBuyMonument(currentViewingPlayer, monumentName, fromDeck);

    if (state.error) {
        console.error('Error buying monument:', state.error);
        alert('Cannot buy monument: ' + state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

/**
 * Discard a card for resources
 */
async function discardCardForResources(cardName, gainGold) {
    if (!currentGameState) return;

    let state;
    if (gainGold) {
        state = await apiActionDiscardCard(currentViewingPlayer, cardName, true);
    } else {
        // For simplicity, default to 2 of first available type
        // TODO: Add UI to choose resource types
        state = await apiActionDiscardCard(currentViewingPlayer, cardName, false, { red: 2 });
    }

    if (state.error) {
        console.error('Error discarding card:', state.error);
        return;
    }

    currentGameState = state;
    renderGame(state, currentViewingPlayer);
}

// ============================================================
// Main Render Function (Updated)
// ============================================================

/**
 * Render playable cards in hand with play buttons
 */
function renderHandCards(hand, isMyTurn) {
    if (!hand) return '';

    return hand.map(card => {
        const typeClass = card.cardType;
        const costStr = card.effects?.cost ?
            Object.entries(card.effects.cost).map(([t, c]) => `${c}${t[0].toUpperCase()}`).join('') :
            'Free';

        return `
            <div class="card ${typeClass} hand-card">
                <div class="card-name">${card.name}</div>
                <div class="card-cost">${costStr}</div>
                ${isMyTurn ? `
                    <div class="hand-card-actions">
                        <button class="play-btn" onclick="event.stopPropagation(); playCard('${card.name}')">Play</button>
                        <button class="discard-btn" onclick="event.stopPropagation(); discardCardForResources('${card.name}', true)">Discard→1G</button>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

/**
 * Render clickable Places of Power for purchase
 */
function renderBuyablePlacesOfPower(placesOfPower, isMyTurn) {
    return placesOfPower.map(card => {
        const costStr = card.effects?.cost ?
            Object.entries(card.effects.cost).map(([t, c]) => `${c}${t[0].toUpperCase()}`).join('') :
            'Free';

        return `
            <div class="card place_of_power ${isMyTurn ? 'buyable' : ''}">
                <div class="card-name">${card.name}</div>
                <div class="card-cost">${costStr}</div>
                ${isMyTurn ? `<button class="buy-btn" onclick="event.stopPropagation(); buyPlaceOfPower('${card.name}')">Buy</button>` : ''}
            </div>
        `;
    }).join('');
}

/**
 * Render clickable Monuments for purchase
 */
function renderBuyableMonuments(monuments, isMyTurn) {
    return monuments.map(card => {
        return `
            <div class="card monument ${isMyTurn ? 'buyable' : ''}">
                <div class="card-name">${card.name}</div>
                <div class="card-cost">4G</div>
                ${isMyTurn ? `<button class="buy-btn" onclick="event.stopPropagation(); buyMonument('${card.name}')">Buy</button>` : ''}
            </div>
        `;
    }).join('');
}

/**
 * Render the game over screen
 */
function renderGameOver(gameState, viewingPlayerId) {
    const victoryResult = gameState.victoryResult;
    if (!victoryResult) return;

    const players = gameState.players;

    // Sort players by points (descending), then by resource value (descending)
    const sortedPlayers = [...players].sort((a, b) => {
        if (b.points !== a.points) return b.points - a.points;
        return b.resourceValue - a.resourceValue;
    });

    let resultText;
    if (victoryResult.isTie) {
        const tiedNames = victoryResult.tiedPlayers.map(pid => `Player ${pid + 1}`).join(' and ');
        resultText = `Game ends in a tie between ${tiedNames}!`;
    } else if (victoryResult.winner !== null) {
        resultText = `Player ${victoryResult.winner + 1} wins!`;
    } else {
        resultText = 'Game Over';
    }

    // Create standings table
    const standingsHtml = sortedPlayers.map((p, i) => {
        const isWinner = victoryResult.winner === p.playerId;
        const rowClass = isWinner ? 'winner' : '';
        return `<tr class="${rowClass}">
            <td>${i + 1}</td>
            <td>Player ${p.playerId + 1}${p.playerId === viewingPlayerId ? ' (You)' : ''}</td>
            <td>${p.points}</td>
            <td>${p.resourceValue}</td>
        </tr>`;
    }).join('');

    // Show game over overlay
    const draftSection = document.getElementById('draft-section');
    draftSection.classList.remove('hidden');
    draftSection.innerHTML = `
        <h2>Game Over</h2>
        <p class="game-result">${resultText}</p>
        <table class="standings">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Player</th>
                    <th>Points</th>
                    <th>Resources</th>
                </tr>
            </thead>
            <tbody>
                ${standingsHtml}
            </tbody>
        </table>
        <button onclick="newGameFromUI()" class="new-game-btn">New Game</button>
    `;

    // Hide other sections
    document.getElementById('income-section').classList.add('hidden');
    document.getElementById('action-section').classList.add('hidden');
}

/**
 * Render the game board for a specific player's view
 */
function renderGame(gameState, viewingPlayerId) {
    // Store for interaction handlers
    currentGameState = gameState;
    currentViewingPlayer = viewingPlayerId;
    // Update polling state to avoid duplicate renders
    lastStateJson = JSON.stringify(gameState);

    // Handle game over
    if (gameState.phase === 'game_over') {
        renderGameOver(gameState, viewingPlayerId);
        return;
    }

    // Phases where we hide player details (not magic item selection - mages are revealed then)
    const hidePlayerDetails = gameState.phase === GamePhase.SETUP ||
        gameState.phase === GamePhase.DRAFTING_ROUND_1 ||
        gameState.phase === GamePhase.DRAFTING_ROUND_2 ||
        gameState.phase === GamePhase.MAGE_SELECTION;

    // Check if it's the player's turn during action phase
    const isActionPhase = gameState.phase === GamePhase.PLAYING && gameState.actionState;
    const isMyTurn = isActionPhase && gameState.actionState.currentPlayer === viewingPlayerId;

    // Render draft section if in draft phase
    renderDraftSection(gameState, viewingPlayerId);

    // Render income section if in income phase
    renderIncomeSection(gameState, viewingPlayerId);

    // Render action section if in playing phase
    renderActionSection(gameState, viewingPlayerId);

    // Update the View As dropdown to match player count
    updateViewAsDropdown(gameState.players.length);

    // Hide/show player areas based on phase
    document.getElementById('player-area').classList.toggle('draft-mode', hidePlayerDetails);
    document.getElementById('opponents-container').classList.toggle('draft-mode', hidePlayerDetails);

    const visibleState = getVisibleState(gameState, viewingPlayerId);

    // Find viewing player and opponent(s)
    const viewingPlayer = visibleState.players.find(p => p.playerId === viewingPlayerId);
    const opponents = visibleState.players.filter(p => p.playerId !== viewingPlayerId);

    // Render all opponents
    const opponentsContainer = document.getElementById('opponents-container');
    opponentsContainer.innerHTML = opponents.map((opp, i) => renderOpponentArea(opp, i)).join('');

    // Render shared zones (with buy buttons if it's our turn)
    if (isActionPhase) {
        document.getElementById('available-places').innerHTML =
            renderBuyablePlacesOfPower(visibleState.availablePlacesOfPower, isMyTurn);
        document.getElementById('available-monuments').innerHTML =
            renderBuyableMonuments(visibleState.availableMonuments, isMyTurn);
    } else {
        document.getElementById('available-places').innerHTML =
            visibleState.availablePlacesOfPower.map(card => renderCard(card)).join('');
        document.getElementById('available-monuments').innerHTML =
            visibleState.availableMonuments.map(card => renderCard(card)).join('');
    }

    document.querySelector('#monument-deck .deck-count').textContent = visibleState.monumentDeckCount;

    // Add "buy from deck" button if it's action phase
    const monumentDeck = document.getElementById('monument-deck');
    if (isMyTurn && visibleState.monumentDeckCount > 0) {
        monumentDeck.classList.add('buyable');
        monumentDeck.onclick = () => buyMonument(null, true);
    } else {
        monumentDeck.classList.remove('buyable');
        monumentDeck.onclick = null;
    }

    document.getElementById('available-magic-items').innerHTML =
        renderFixedSlots(visibleState.availableMagicItems, ALL_MAGIC_ITEMS);
    document.getElementById('available-scrolls').innerHTML =
        renderFixedSlots(visibleState.availableScrolls, ALL_SCROLLS);

    // Render player area (with abilities shown during action phase)
    document.getElementById('player-label').textContent = `Player ${viewingPlayerId + 1} (You) - ${viewingPlayer.points || 0} VP`;
    document.getElementById('player-resources').innerHTML = renderPlayerResources(viewingPlayer.resources);
    document.getElementById('player-controlled').innerHTML = renderControlledCards(viewingPlayer, isActionPhase, isMyTurn);

    // Update player deck count
    document.querySelector('#player-deck .deck-count').textContent = viewingPlayer.deckCount;

    // Render player discard pile
    document.querySelector('#player-discard .discard-cards').innerHTML =
        viewingPlayer.discard.map(card => renderCard(card)).join('');

    // Render player scrolls
    document.getElementById('player-scrolls').innerHTML =
        viewingPlayer.scrolls.map(card => renderCard(card)).join('');

    // First player token for player
    document.getElementById('player-token-slot').innerHTML = renderFirstPlayerToken(viewingPlayer);

    // Render player's hand (with play buttons if it's our turn)
    const handHtml = isActionPhase ?
        renderHandCards(viewingPlayer.hand, isMyTurn) :
        (viewingPlayer.hand ? viewingPlayer.hand.map(card => renderCard(card)).join('') : '');
    document.querySelector('#player-hand .hand-cards').innerHTML = handHtml;

    // Update debug panels
    document.getElementById('visible-state').textContent =
        JSON.stringify(visibleState, null, 2);
    // Full state is fetched separately from debug endpoint
    updateFullStateDebug();
}

/**
 * Fetch and display full game state in debug panel
 */
async function updateFullStateDebug() {
    const fullState = await apiGetFullState();
    const el = document.getElementById('full-state');
    if (fullState && !fullState.error) {
        el.textContent = JSON.stringify(fullState, null, 2);
    } else {
        el.textContent = '(Debug endpoint disabled or no game)';
    }
}

/**
 * Toggle debug panel visibility
 */
function toggleDebug() {
    const panel = document.getElementById('debug-panel');
    const button = document.getElementById('debug-toggle');
    panel.classList.toggle('collapsed');
    document.body.classList.toggle('debug-collapsed');
    button.textContent = panel.classList.contains('collapsed') ? '◀ Debug' : 'Debug ▶';
}

/**
 * Update "Play As" dropdown based on number of players selected
 */
function updatePlayAsOptions() {
    const numPlayers = parseInt(document.getElementById('new-game-players').value, 10);
    const dropdown = document.getElementById('play-as-player');
    const currentValue = parseInt(dropdown.value, 10);

    dropdown.innerHTML = '';
    for (let i = 0; i < numPlayers; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = `Player ${i + 1}`;
        dropdown.appendChild(option);
    }

    // Keep current selection if still valid
    if (currentValue < numPlayers) {
        dropdown.value = currentValue;
    }
}

/**
 * Start a new game via API
 */
async function newGameFromUI() {
    const numPlayers = parseInt(document.getElementById('new-game-players').value, 10);
    const playAs = parseInt(document.getElementById('play-as-player').value, 10);
    await startNewGame(numPlayers, playAs);
}

/**
 * Switch which player we're viewing as
 */
function switchViewingPlayer(playerId) {
    currentViewingPlayer = parseInt(playerId, 10);
    if (currentGameState) {
        renderGame(currentGameState, currentViewingPlayer);
    }
}

/**
 * Update the "View As" dropdown to match the number of players
 */
function updateViewAsDropdown(numPlayers) {
    const dropdown = document.getElementById('view-as-player');
    dropdown.innerHTML = '';
    for (let i = 0; i < numPlayers; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = `Player ${i + 1}`;
        dropdown.appendChild(option);
    }
    dropdown.value = currentViewingPlayer;
}

// ============================================================
// Polling System
// ============================================================

let pollingInterval = null;
let lastStateJson = null;

/**
 * Start polling for game state updates
 */
function startPolling(intervalMs = 500) {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }

    pollingInterval = setInterval(async () => {
        try {
            const state = await apiGetState(currentViewingPlayer);
            if (!state || state.error) return;

            // Only re-render if state has changed
            const stateJson = JSON.stringify(state);
            if (stateJson !== lastStateJson) {
                lastStateJson = stateJson;
                currentGameState = state;
                renderGame(state, currentViewingPlayer);
                console.log('State updated from poll');
            }
        } catch (e) {
            // Server unavailable, ignore
        }
    }, intervalMs);

    console.log(`Polling started (${intervalMs}ms interval)`);
}

/**
 * Stop polling
 */
function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
        console.log('Polling stopped');
    }
}

// Initialize: try to load existing game, otherwise show welcome state
document.addEventListener('DOMContentLoaded', async () => {
    const hasGame = await loadCurrentGame();
    if (!hasGame) {
        // No game in progress - show a message or auto-start
        console.log('No game in progress. Click "New Game" to start.');
        // For convenience, auto-start a 2-player game
        await startNewGame(2);
    }

    // Start polling for updates
    startPolling(500);
});
