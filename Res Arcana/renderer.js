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
    PLAYING: 'playing'
};

// Current game state and viewing player (for interaction handlers)
let currentGameState = null;
let currentViewingPlayer = 0;

// ============================================================
// API Functions
// ============================================================

async function apiNewGame(numPlayers = 2) {
    const response = await fetch('/api/new-game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ numPlayers })
    });
    return response.json();
}

async function apiGetState() {
    const response = await fetch('/api/state');
    if (response.status === 404) return null;
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

async function startNewGame(numPlayers = 2) {
    const state = await apiNewGame(numPlayers);
    if (state.error) {
        console.error('Error starting game:', state.error);
        return;
    }
    currentGameState = state;
    // Keep viewing player from selector, but clamp to valid range
    if (currentViewingPlayer >= numPlayers) {
        currentViewingPlayer = 0;
    }
    renderGame(state, currentViewingPlayer);
}

async function loadCurrentGame() {
    const state = await apiGetState();
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
 * Create HTML for a single card
 */
function renderCard(card, controlled = null) {
    const tappedClass = controlled?.tapped ? 'tapped' : '';
    const typeClass = card.cardType;
    const resourcesHtml = controlled ? renderCardResources(controlled.resources) : '';

    return `
        <div class="card ${typeClass} ${tappedClass}">
            <div class="card-name">${card.name}</div>
            <div class="card-type">${card.cardType.replace('_', ' ')}</div>
            ${resourcesHtml}
        </div>
    `;
}

/**
 * Create HTML for a controlled card (card on table with state)
 */
function renderControlledCard(controlledCard) {
    return renderCard(controlledCard.card, controlledCard);
}

/**
 * Render all controlled cards for a player
 */
function renderControlledCards(player) {
    let html = '';

    // Mage and Magic Item first (skip if empty/placeholder)
    if (player.mage?.card?.name) {
        html += renderControlledCard(player.mage);
    }
    if (player.magicItem?.card?.name) {
        html += renderControlledCard(player.magicItem);
    }

    // Then artifacts
    for (const artifact of player.artifacts) {
        html += renderControlledCard(artifact);
    }

    // Then places of power
    for (const pop of player.placesOfPower) {
        html += renderControlledCard(pop);
    }

    // Then monuments
    for (const monument of player.monuments) {
        html += renderControlledCard(monument);
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
    const label = `Player ${playerNum}`;
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
            <div class="card-type">${card.cardType.replace('_', ' ')}</div>
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

    // Hide section during playing phase
    if (phase === GamePhase.PLAYING || !phase) {
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
// Main Render Function (Updated)
// ============================================================

/**
 * Render the game board for a specific player's view
 */
function renderGame(gameState, viewingPlayerId) {
    // Store for interaction handlers
    currentGameState = gameState;
    currentViewingPlayer = viewingPlayerId;

    // Phases where we hide player details (not magic item selection - mages are revealed then)
    const hidePlayerDetails = gameState.phase === GamePhase.SETUP ||
        gameState.phase === GamePhase.DRAFTING_ROUND_1 ||
        gameState.phase === GamePhase.DRAFTING_ROUND_2 ||
        gameState.phase === GamePhase.MAGE_SELECTION;

    // Render draft section if in draft phase
    renderDraftSection(gameState, viewingPlayerId);

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

    // Render shared zones
    document.getElementById('available-places').innerHTML =
        visibleState.availablePlacesOfPower.map(card => renderCard(card)).join('');
    document.getElementById('available-monuments').innerHTML =
        visibleState.availableMonuments.map(card => renderCard(card)).join('');
    document.querySelector('#monument-deck .deck-count').textContent = visibleState.monumentDeckCount;
    document.getElementById('available-magic-items').innerHTML =
        renderFixedSlots(visibleState.availableMagicItems, ALL_MAGIC_ITEMS);
    document.getElementById('available-scrolls').innerHTML =
        renderFixedSlots(visibleState.availableScrolls, ALL_SCROLLS);

    // Render player area
    document.getElementById('player-label').textContent = `Player ${viewingPlayerId + 1} (You)`;
    document.getElementById('player-resources').innerHTML = renderPlayerResources(viewingPlayer.resources);
    document.getElementById('player-controlled').innerHTML = renderControlledCards(viewingPlayer);

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

    // Render player's hand (visible to them)
    const handHtml = viewingPlayer.hand ?
        viewingPlayer.hand.map(card => renderCard(card)).join('') :
        '';
    document.querySelector('#player-hand .hand-cards').innerHTML = handHtml;

    // Update debug panels
    document.getElementById('visible-state').textContent =
        JSON.stringify(visibleState, null, 2);
    document.getElementById('full-state').textContent =
        JSON.stringify(gameState, null, 2);
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
    currentViewingPlayer = playAs;
    await startNewGame(numPlayers);
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

// Initialize: try to load existing game, otherwise show welcome state
document.addEventListener('DOMContentLoaded', async () => {
    const hasGame = await loadCurrentGame();
    if (!hasGame) {
        // No game in progress - show a message or auto-start
        console.log('No game in progress. Click "New Game" to start.');
        // For convenience, auto-start a 2-player game
        await startNewGame(2);
    }
});
