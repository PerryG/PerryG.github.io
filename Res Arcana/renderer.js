// Renderer for Res Arcana game state

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

    // Mage and Magic Item first
    html += renderControlledCard(player.mage);
    html += renderControlledCard(player.magicItem);

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
    const label = opponent.playerId !== undefined ? `Opponent ${index + 1}` : 'Opponent';
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

/**
 * Render the game board for a specific player's view
 */
function renderGame(gameState, viewingPlayerId) {
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
        visibleState.availableMagicItems.map(card => renderCard(card)).join('');
    document.getElementById('available-scrolls').innerHTML =
        visibleState.availableScrolls.map(card => renderCard(card)).join('');

    // Render player area
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
 * Switch between sample states (2p, 3p, 4p)
 */
function switchSampleState(stateKey) {
    sampleGameState = sampleStates[stateKey];
    renderGame(sampleGameState, 0);
}

// Initialize with sample state, viewing as player 0
document.addEventListener('DOMContentLoaded', () => {
    renderGame(sampleGameState, 0);
});
