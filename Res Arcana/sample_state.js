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
    MAGE: 'mage',
    SCROLL: 'scroll'
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
    monument3: { name: 'Obelisk', cardType: CardType.MONUMENT },

    // Additional Magic Items (for available pool)
    magicItem3: { name: 'Divination', cardType: CardType.MAGIC_ITEM },
    magicItem4: { name: 'Protection', cardType: CardType.MAGIC_ITEM },
    magicItem5: { name: 'Transmutation', cardType: CardType.MAGIC_ITEM },
    magicItem6: { name: 'Destruction', cardType: CardType.MAGIC_ITEM },
    magicItem7: { name: 'Resurrection', cardType: CardType.MAGIC_ITEM },
    magicItem8: { name: 'Conjuration', cardType: CardType.MAGIC_ITEM },
    magicItem9: { name: 'Illusion', cardType: CardType.MAGIC_ITEM },
    magicItem10: { name: 'Enchantment', cardType: CardType.MAGIC_ITEM },

    // Scrolls
    scroll1: { name: 'Cursed Land', cardType: CardType.SCROLL },
    scroll2: { name: 'Elemental Spring', cardType: CardType.SCROLL },
    scroll3: { name: 'Judgment', cardType: CardType.SCROLL },
    scroll4: { name: 'Pyrrhic Victory', cardType: CardType.SCROLL },
    scroll5: { name: 'Dark Pact', cardType: CardType.SCROLL },
    scroll6: { name: 'Sacred Rite', cardType: CardType.SCROLL },
    scroll7: { name: 'Blood Oath', cardType: CardType.SCROLL },
    scroll8: { name: 'Binding Word', cardType: CardType.SCROLL },
    scroll9: { name: 'Final Rest', cardType: CardType.SCROLL },
    scroll10: { name: 'Spirit Call', cardType: CardType.SCROLL }
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
            scrolls: [
                sampleCards.scroll1
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
            scrolls: [
                sampleCards.scroll2
            ],
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
        sampleCards.pop1,
        sampleCards.pop2,
        sampleCards.pop3,
        sampleCards.pop4
    ],
    availableMagicItems: [
        sampleCards.magicItem3,
        sampleCards.magicItem4,
        sampleCards.magicItem5,
        sampleCards.magicItem6,
        sampleCards.magicItem7,
        sampleCards.magicItem8,
        sampleCards.magicItem9,
        sampleCards.magicItem10
    ],
    availableScrolls: [
        sampleCards.scroll3,
        sampleCards.scroll4,
        sampleCards.scroll5,
        sampleCards.scroll6,
        sampleCards.scroll7,
        sampleCards.scroll8,
        sampleCards.scroll9,
        sampleCards.scroll10
    ],
    monumentDeck: [
        // Face down, contents hidden
        {}, {}, {}, {}
    ]
};
