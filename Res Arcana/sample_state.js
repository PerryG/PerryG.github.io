// Sample game state for testing rendering
// This mirrors the Python GameState structure

const ResourceType = {
    RED: 'red',
    BLUE: 'blue',
    GREEN: 'green',
    BLACK: 'black',
    GOLD: 'gold'
};

const CardType = {
    ARTIFACT: 'artifact',
    PLACE_OF_POWER: 'place_of_power',
    MONUMENT: 'monument',
    MAGIC_ITEM: 'magic_item',
    MAGE: 'mage'
};

// Sample cards (just names and types for now)
const sampleCards = {
    // Mages
    mage1: { name: 'Duelist', cardType: CardType.MAGE },
    mage2: { name: 'Necromancer', cardType: CardType.MAGE },

    // Magic Items
    magicItem1: { name: 'Calm', cardType: CardType.MAGIC_ITEM },
    magicItem2: { name: 'Life', cardType: CardType.MAGIC_ITEM },

    // Artifacts
    artifact1: { name: 'Dragon Egg', cardType: CardType.ARTIFACT },
    artifact2: { name: 'Cursed Forge', cardType: CardType.ARTIFACT },
    artifact3: { name: 'Hawk', cardType: CardType.ARTIFACT },
    artifact4: { name: 'Fiery Whip', cardType: CardType.ARTIFACT },
    artifact5: { name: 'Guard Dog', cardType: CardType.ARTIFACT },
    artifact6: { name: 'Vault', cardType: CardType.ARTIFACT },
    artifact7: { name: 'Tree of Life', cardType: CardType.ARTIFACT },
    artifact8: { name: 'Windup Man', cardType: CardType.ARTIFACT },

    // Places of Power
    pop1: { name: 'Coral Castle', cardType: CardType.PLACE_OF_POWER },
    pop2: { name: 'Catacombs', cardType: CardType.PLACE_OF_POWER },
    pop3: { name: 'Sunken Reef', cardType: CardType.PLACE_OF_POWER },
    pop4: { name: 'Sacred Grove', cardType: CardType.PLACE_OF_POWER },

    // Monuments
    monument1: { name: 'Dragon\'s Lair', cardType: CardType.MONUMENT },
    monument2: { name: 'Great Pyramid', cardType: CardType.MONUMENT },
    monument3: { name: 'Obelisk', cardType: CardType.MONUMENT }
};

// Sample game state
const sampleGameState = {
    players: [
        {
            playerId: 0,
            mage: {
                card: sampleCards.mage1,
                tapped: false,
                resources: {}
            },
            magicItem: {
                card: sampleCards.magicItem1,
                tapped: true,
                resources: {}
            },
            artifacts: [
                {
                    card: sampleCards.artifact1,
                    tapped: false,
                    resources: { [ResourceType.RED]: 2 }
                },
                {
                    card: sampleCards.artifact2,
                    tapped: true,
                    resources: { [ResourceType.BLACK]: 1 }
                }
            ],
            monuments: [],
            placesOfPower: [
                {
                    card: sampleCards.pop1,
                    tapped: false,
                    resources: { [ResourceType.BLUE]: 3, [ResourceType.GOLD]: 1 }
                }
            ],
            hand: [
                sampleCards.artifact3,
                sampleCards.artifact4,
                sampleCards.artifact5
            ],
            deck: [
                sampleCards.artifact6,
                sampleCards.artifact7
            ],
            discard: [
                sampleCards.artifact8,
                sampleCards.artifact6,
                sampleCards.artifact7
            ],
            resources: {
                [ResourceType.RED]: 1,
                [ResourceType.BLUE]: 2,
                [ResourceType.GREEN]: 0,
                [ResourceType.BLACK]: 1,
                [ResourceType.GOLD]: 3
            },
            hasFirstPlayerToken: true,
            firstPlayerTokenFaceUp: false
        },
        {
            playerId: 1,
            mage: {
                card: sampleCards.mage2,
                tapped: false,
                resources: {}
            },
            magicItem: {
                card: sampleCards.magicItem2,
                tapped: false,
                resources: {}
            },
            artifacts: [
                {
                    card: sampleCards.artifact3,
                    tapped: false,
                    resources: { [ResourceType.GREEN]: 2 }
                }
            ],
            monuments: [
                {
                    card: sampleCards.monument1,
                    tapped: false,
                    resources: {}
                }
            ],
            placesOfPower: [],
            hand: [
                sampleCards.artifact4,
                sampleCards.artifact5
            ],
            deck: [
                sampleCards.artifact6,
                sampleCards.artifact7
            ],
            discard: [
                sampleCards.artifact8
            ],
            resources: {
                [ResourceType.RED]: 0,
                [ResourceType.BLUE]: 1,
                [ResourceType.GREEN]: 3,
                [ResourceType.BLACK]: 2,
                [ResourceType.GOLD]: 0
            },
            hasFirstPlayerToken: false,
            firstPlayerTokenFaceUp: true
        }
    ],
    availableMonuments: [
        sampleCards.monument2,
        sampleCards.monument3
    ],
    availablePlacesOfPower: [
        sampleCards.pop2,
        sampleCards.pop3,
        sampleCards.pop4
    ],
    monumentDeck: [
        // Face down, contents hidden
        {}, {}, {}, {}
    ]
};
