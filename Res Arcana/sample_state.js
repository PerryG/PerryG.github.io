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

// Additional mages for 3-4 player games
sampleCards.mage3 = { name: 'Alchemist', cardType: CardType.MAGE };
sampleCards.mage4 = { name: 'Druid', cardType: CardType.MAGE };

// 2-player sample game state
const sampleGameState2p = {
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

// 3-player sample game state
// Demonstrates: opponent has the first player marker
const sampleGameState3p = {
    players: [
        {
            playerId: 0,
            mage: { card: sampleCards.mage1, tapped: false, resources: {} },
            magicItem: { card: sampleCards.magicItem1, tapped: false, resources: {} },
            artifacts: [
                { card: sampleCards.artifact1, tapped: false, resources: { [ResourceType.RED]: 2 } }
            ],
            monuments: [],
            placesOfPower: [],
            scrolls: [sampleCards.scroll1],
            hand: [sampleCards.artifact2, sampleCards.artifact3],
            deck: [sampleCards.artifact4, sampleCards.artifact5],
            discard: [sampleCards.artifact6],
            resources: { [ResourceType.RED]: 1, [ResourceType.BLUE]: 2, [ResourceType.GREEN]: 0, [ResourceType.BLACK]: 1, [ResourceType.GOLD]: 3 },
            hasFirstPlayerToken: false,  // You don't have it
            firstPlayerTokenFaceUp: true
        },
        {
            playerId: 1,
            mage: { card: sampleCards.mage2, tapped: false, resources: {} },
            magicItem: { card: sampleCards.magicItem2, tapped: true, resources: {} },
            artifacts: [
                { card: sampleCards.artifact2, tapped: false, resources: { [ResourceType.BLACK]: 1 } }
            ],
            monuments: [{ card: sampleCards.monument1, tapped: false, resources: {} }],
            placesOfPower: [],
            scrolls: [],
            hand: [sampleCards.artifact3],
            deck: [sampleCards.artifact4, sampleCards.artifact5],
            discard: [],
            resources: { [ResourceType.RED]: 0, [ResourceType.BLUE]: 1, [ResourceType.GREEN]: 3, [ResourceType.BLACK]: 2, [ResourceType.GOLD]: 0 },
            hasFirstPlayerToken: true,  // Opponent 1 has the first player marker
            firstPlayerTokenFaceUp: true
        },
        {
            playerId: 2,
            mage: { card: sampleCards.mage3, tapped: false, resources: {} },
            magicItem: { card: sampleCards.magicItem3, tapped: false, resources: {} },
            artifacts: [
                { card: sampleCards.artifact3, tapped: true, resources: { [ResourceType.GREEN]: 2 } }
            ],
            monuments: [],
            placesOfPower: [{ card: sampleCards.pop1, tapped: false, resources: { [ResourceType.BLUE]: 2 } }],
            scrolls: [sampleCards.scroll2],
            hand: [sampleCards.artifact4, sampleCards.artifact5],
            deck: [sampleCards.artifact6],
            discard: [sampleCards.artifact1],
            resources: { [ResourceType.RED]: 2, [ResourceType.BLUE]: 0, [ResourceType.GREEN]: 1, [ResourceType.BLACK]: 0, [ResourceType.GOLD]: 2 },
            hasFirstPlayerToken: false,
            firstPlayerTokenFaceUp: true
        }
    ],
    availableMonuments: [sampleCards.monument2],
    availablePlacesOfPower: [sampleCards.pop2, sampleCards.pop3],
    availableMagicItems: [sampleCards.magicItem4, sampleCards.magicItem5, sampleCards.magicItem6],
    availableScrolls: [sampleCards.scroll3, sampleCards.scroll4],
    monumentDeck: [{}, {}, {}]
};

// 4-player sample game state
// Demonstrates: (a) your deck empty, (b) opponent 1 deck empty, (c) opponent 2 hand empty
const sampleGameState4p = {
    players: [
        {
            playerId: 0,
            mage: { card: sampleCards.mage1, tapped: false, resources: {} },
            magicItem: { card: sampleCards.magicItem1, tapped: false, resources: {} },
            artifacts: [
                { card: sampleCards.artifact1, tapped: false, resources: { [ResourceType.RED]: 1 } }
            ],
            monuments: [],
            placesOfPower: [],
            scrolls: [],
            hand: [sampleCards.artifact2, sampleCards.artifact3],
            deck: [],  // (a) Your deck is empty
            discard: [sampleCards.artifact4, sampleCards.artifact5],
            resources: { [ResourceType.RED]: 1, [ResourceType.BLUE]: 2, [ResourceType.GREEN]: 0, [ResourceType.BLACK]: 1, [ResourceType.GOLD]: 3 },
            hasFirstPlayerToken: true,
            firstPlayerTokenFaceUp: true
        },
        {
            playerId: 1,
            mage: { card: sampleCards.mage2, tapped: false, resources: {} },
            magicItem: { card: sampleCards.magicItem2, tapped: true, resources: {} },
            artifacts: [
                { card: sampleCards.artifact2, tapped: false, resources: {} }
            ],
            monuments: [],
            placesOfPower: [],
            scrolls: [sampleCards.scroll1],
            hand: [sampleCards.artifact3],
            deck: [],  // (b) Opponent 1 deck is empty
            discard: [sampleCards.artifact4, sampleCards.artifact5, sampleCards.artifact6],
            resources: { [ResourceType.RED]: 0, [ResourceType.BLUE]: 1, [ResourceType.GREEN]: 3, [ResourceType.BLACK]: 2, [ResourceType.GOLD]: 0 },
            hasFirstPlayerToken: false,
            firstPlayerTokenFaceUp: true
        },
        {
            playerId: 2,
            mage: { card: sampleCards.mage3, tapped: false, resources: {} },
            magicItem: { card: sampleCards.magicItem3, tapped: false, resources: {} },
            artifacts: [
                { card: sampleCards.artifact3, tapped: true, resources: { [ResourceType.GREEN]: 2 } }
            ],
            monuments: [{ card: sampleCards.monument1, tapped: false, resources: {} }],
            placesOfPower: [],
            scrolls: [],
            hand: [],  // (c) Opponent 2 hand is empty
            deck: [sampleCards.artifact5, sampleCards.artifact6],
            discard: [sampleCards.artifact1],
            resources: { [ResourceType.RED]: 2, [ResourceType.BLUE]: 0, [ResourceType.GREEN]: 1, [ResourceType.BLACK]: 0, [ResourceType.GOLD]: 2 },
            hasFirstPlayerToken: false,
            firstPlayerTokenFaceUp: true
        },
        {
            playerId: 3,
            mage: { card: sampleCards.mage4, tapped: false, resources: {} },
            magicItem: { card: sampleCards.magicItem4, tapped: false, resources: {} },
            artifacts: [
                { card: sampleCards.artifact4, tapped: false, resources: { [ResourceType.BLACK]: 1 } }
            ],
            monuments: [],
            placesOfPower: [{ card: sampleCards.pop1, tapped: false, resources: { [ResourceType.BLUE]: 3 } }],
            scrolls: [sampleCards.scroll2],
            hand: [sampleCards.artifact5, sampleCards.artifact6],
            deck: [sampleCards.artifact1],
            discard: [],
            resources: { [ResourceType.RED]: 0, [ResourceType.BLUE]: 2, [ResourceType.GREEN]: 2, [ResourceType.BLACK]: 1, [ResourceType.GOLD]: 1 },
            hasFirstPlayerToken: false,
            firstPlayerTokenFaceUp: true
        }
    ],
    availableMonuments: [sampleCards.monument2],
    availablePlacesOfPower: [sampleCards.pop2],
    availableMagicItems: [sampleCards.magicItem5, sampleCards.magicItem6],
    availableScrolls: [sampleCards.scroll3, sampleCards.scroll4],
    monumentDeck: [{}, {}]
};

// Draft Phase sample states

// Draft Round 1 - player has 4 cards to choose from
const sampleDraftRound1 = {
    phase: 'drafting_round_1',
    players: [
        {
            playerId: 0,
            mage: { card: { name: '', cardType: CardType.MAGE }, tapped: false, resources: {} },
            magicItem: { card: { name: '', cardType: CardType.MAGIC_ITEM }, tapped: false, resources: {} },
            artifacts: [],
            monuments: [],
            placesOfPower: [],
            scrolls: [],
            hand: [],
            deck: [],
            discard: [],
            resources: {},
            hasFirstPlayerToken: true,
            firstPlayerTokenFaceUp: true
        },
        {
            playerId: 1,
            mage: { card: { name: '', cardType: CardType.MAGE }, tapped: false, resources: {} },
            magicItem: { card: { name: '', cardType: CardType.MAGIC_ITEM }, tapped: false, resources: {} },
            artifacts: [],
            monuments: [],
            placesOfPower: [],
            scrolls: [],
            hand: [],
            deck: [],
            discard: [],
            resources: {},
            hasFirstPlayerToken: false,
            firstPlayerTokenFaceUp: true
        }
    ],
    draftState: {
        cardsToPick: {
            0: [sampleCards.artifact1, sampleCards.artifact2, sampleCards.artifact3, sampleCards.artifact4],
            1: [sampleCards.artifact5, sampleCards.artifact6, sampleCards.artifact7, sampleCards.artifact8]
        },
        draftedCards: {
            0: [],
            1: []
        },
        mageOptions: {
            0: [sampleCards.mage1, sampleCards.mage2],
            1: [sampleCards.mage3, sampleCards.mage4]
        },
        selectedMage: {
            0: null,
            1: null
        }
    },
    availableMonuments: [sampleCards.monument2, sampleCards.monument3],
    availablePlacesOfPower: [sampleCards.pop1, sampleCards.pop2, sampleCards.pop3, sampleCards.pop4],
    availableMagicItems: [
        sampleCards.magicItem1, sampleCards.magicItem2, sampleCards.magicItem3, sampleCards.magicItem4,
        sampleCards.magicItem5, sampleCards.magicItem6, sampleCards.magicItem7, sampleCards.magicItem8
    ],
    availableScrolls: [sampleCards.scroll1, sampleCards.scroll2, sampleCards.scroll3, sampleCards.scroll4],
    monumentDeck: [{}, {}, {}, {}, {}]  // 2 players: 7 total (2 face-up + 5 in deck)
};

// Mage Selection phase - player has drafted 8 cards, now picks mage
const sampleMageSelection = {
    phase: 'mage_selection',
    players: [
        {
            playerId: 0,
            mage: { card: { name: '', cardType: CardType.MAGE }, tapped: false, resources: {} },
            magicItem: { card: { name: '', cardType: CardType.MAGIC_ITEM }, tapped: false, resources: {} },
            artifacts: [],
            monuments: [],
            placesOfPower: [],
            scrolls: [],
            hand: [],
            deck: [],
            discard: [],
            resources: {},
            hasFirstPlayerToken: true,
            firstPlayerTokenFaceUp: true
        },
        {
            playerId: 1,
            mage: { card: { name: '', cardType: CardType.MAGE }, tapped: false, resources: {} },
            magicItem: { card: { name: '', cardType: CardType.MAGIC_ITEM }, tapped: false, resources: {} },
            artifacts: [],
            monuments: [],
            placesOfPower: [],
            scrolls: [],
            hand: [],
            deck: [],
            discard: [],
            resources: {},
            hasFirstPlayerToken: false,
            firstPlayerTokenFaceUp: true
        }
    ],
    draftState: {
        cardsToPick: { 0: [], 1: [] },
        draftedCards: {
            0: [sampleCards.artifact1, sampleCards.artifact2, sampleCards.artifact3, sampleCards.artifact4,
                sampleCards.artifact5, sampleCards.artifact6, sampleCards.artifact7, sampleCards.artifact8],
            1: [sampleCards.artifact1, sampleCards.artifact2, sampleCards.artifact3, sampleCards.artifact4,
                sampleCards.artifact5, sampleCards.artifact6, sampleCards.artifact7, sampleCards.artifact8]
        },
        mageOptions: {
            0: [sampleCards.mage1, sampleCards.mage2],
            1: [sampleCards.mage3, sampleCards.mage4]
        },
        selectedMage: {
            0: null,
            1: null
        }
    },
    availableMonuments: [sampleCards.monument2, sampleCards.monument3],
    availablePlacesOfPower: [sampleCards.pop1, sampleCards.pop2, sampleCards.pop3, sampleCards.pop4],
    availableMagicItems: [
        sampleCards.magicItem1, sampleCards.magicItem2, sampleCards.magicItem3, sampleCards.magicItem4,
        sampleCards.magicItem5, sampleCards.magicItem6, sampleCards.magicItem7, sampleCards.magicItem8
    ],
    availableScrolls: [sampleCards.scroll1, sampleCards.scroll2, sampleCards.scroll3, sampleCards.scroll4],
    monumentDeck: [{}, {}, {}, {}, {}]  // 2 players: 7 total (2 face-up + 5 in deck)
};

// Magic Item Selection phase - player 1 (last in turn order) picks first
const sampleMagicItemSelection = {
    phase: 'magic_item_selection',
    players: [
        {
            playerId: 0,
            mage: { card: sampleCards.mage1, tapped: false, resources: {} },
            magicItem: { card: { name: '', cardType: CardType.MAGIC_ITEM }, tapped: false, resources: {} },
            artifacts: [],
            monuments: [],
            placesOfPower: [],
            scrolls: [],
            hand: [],
            deck: [],
            discard: [],
            resources: {},
            hasFirstPlayerToken: true,
            firstPlayerTokenFaceUp: true
        },
        {
            playerId: 1,
            mage: { card: sampleCards.mage3, tapped: false, resources: {} },
            magicItem: { card: { name: '', cardType: CardType.MAGIC_ITEM }, tapped: false, resources: {} },
            artifacts: [],
            monuments: [],
            placesOfPower: [],
            scrolls: [],
            hand: [],
            deck: [],
            discard: [],
            resources: {},
            hasFirstPlayerToken: false,
            firstPlayerTokenFaceUp: true
        }
    ],
    draftState: {
        cardsToPick: { 0: [], 1: [] },
        draftedCards: {
            0: [sampleCards.artifact1, sampleCards.artifact2, sampleCards.artifact3, sampleCards.artifact4,
                sampleCards.artifact5, sampleCards.artifact6, sampleCards.artifact7, sampleCards.artifact8],
            1: [sampleCards.artifact1, sampleCards.artifact2, sampleCards.artifact3, sampleCards.artifact4,
                sampleCards.artifact5, sampleCards.artifact6, sampleCards.artifact7, sampleCards.artifact8]
        },
        mageOptions: {
            0: [sampleCards.mage1, sampleCards.mage2],
            1: [sampleCards.mage3, sampleCards.mage4]
        },
        selectedMage: {
            0: sampleCards.mage1,
            1: sampleCards.mage3
        },
        magicItemSelector: 1  // Player 1 picks first (last in turn order)
    },
    availableMonuments: [sampleCards.monument2, sampleCards.monument3],
    availablePlacesOfPower: [sampleCards.pop1, sampleCards.pop2, sampleCards.pop3, sampleCards.pop4],
    availableMagicItems: [
        sampleCards.magicItem1, sampleCards.magicItem2, sampleCards.magicItem3, sampleCards.magicItem4,
        sampleCards.magicItem5, sampleCards.magicItem6, sampleCards.magicItem7, sampleCards.magicItem8
    ],
    availableScrolls: [sampleCards.scroll1, sampleCards.scroll2, sampleCards.scroll3, sampleCards.scroll4],
    monumentDeck: [{}, {}, {}, {}, {}]  // 2 players: 7 total (2 face-up + 5 in deck)
};

// All sample states
const sampleStates = {
    '2p': sampleGameState2p,
    '3p': sampleGameState3p,
    '4p': sampleGameState4p,
    'draft1': sampleDraftRound1,
    'mage': sampleMageSelection,
    'magic_item': sampleMagicItemSelection
};

// Current active state (default to 2p)
let sampleGameState = sampleGameState2p;
