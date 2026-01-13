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
 * Render the game board for a specific player's view
 */
function renderGame(gameState, viewingPlayerId) {
    const visibleState = getVisibleState(gameState, viewingPlayerId);

    // Find viewing player and opponent(s)
    const viewingPlayer = visibleState.players.find(p => p.playerId === viewingPlayerId);
    const opponents = visibleState.players.filter(p => p.playerId !== viewingPlayerId);

    // For now, just show first opponent (2-player focused)
    const opponent = opponents[0];

    // Render opponent area
    document.getElementById('opponent-resources').innerHTML = renderPlayerResources(opponent.resources);
    document.getElementById('opponent-controlled').innerHTML = renderControlledCards(opponent);

    // Update opponent deck and hand counts
    document.querySelector('#opponent-deck .deck-count').textContent = opponent.deckCount;
    document.querySelector('#opponent-hand .deck-count').textContent = opponent.handCount;

    // Render opponent discard pile
    document.querySelector('#opponent-discard .discard-cards').innerHTML =
        opponent.discard.map(card => renderCard(card)).join('');

    // First player token for opponent
    document.getElementById('opponent-token-slot').innerHTML = renderFirstPlayerToken(opponent);

    // Render shared zones
    document.getElementById('available-places').innerHTML =
        visibleState.availablePlacesOfPower.map(card => renderCard(card)).join('');
    document.getElementById('available-monuments').innerHTML =
        visibleState.availableMonuments.map(card => renderCard(card)).join('');
    document.querySelector('#monument-deck .deck-count').textContent = visibleState.monumentDeckCount;

    // Render player area
    document.getElementById('player-resources').innerHTML = renderPlayerResources(viewingPlayer.resources);
    document.getElementById('player-controlled').innerHTML = renderControlledCards(viewingPlayer);

    // Update player deck count
    document.querySelector('#player-deck .deck-count').textContent = viewingPlayer.deckCount;

    // Render player discard pile
    document.querySelector('#player-discard .discard-cards').innerHTML =
        viewingPlayer.discard.map(card => renderCard(card)).join('');

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

// Initialize with sample state, viewing as player 0
document.addEventListener('DOMContentLoaded', () => {
    renderGame(sampleGameState, 0);
});
