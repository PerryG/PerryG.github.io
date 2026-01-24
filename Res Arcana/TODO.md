# Res Arcana Implementation Status

## Not Implemented

### Income (2 cards)
| Card | Issue |
|------|-------|
| **Vault** | Conditional income: "if gold left on card, gain 2 non-gold" - condition not checked |
| **Windup Man** | Conditional income: "add 2 of each type already on card" - requires checking resources on card |

### Effect Types (3 issues)
| Effect | Issue | Cards Using It |
|--------|-------|----------------|
| **reorder_deck** | Returns a flag but doesn't actually reorder - needs UI | Hawk |
| **draw_discard** | Draws cards but discard portion not implemented - needs UI for player to choose what to discard | Shadowy Figure |
| **play_card** | Mostly works, but discount/free logic may need verification | Crypt, Dragon Egg, Dragon Teeth |

### Attack/Reaction System (affects many cards)
| Issue | Details |
|-------|---------|
| **Reactions don't pause game** | When an attack happens, the game doesn't pause for defender to choose: pay, avoid, or use reaction. Currently assumes immediate resolution. |
| **Reaction abilities not executed** | `get_attack_reactions()` finds reactions, but they're never actually triggered/executed |

**Cards with reaction abilities affected:**
- Dancing Sword, Elemental Spring, Guard Dog, Tree of Life, Golden Lion (reaction: tap/pay → ignore attack)
- Demon Slayer (reaction: ignore demon attacks for free)
- Vial of Light (reaction: when any artifact destroyed → gain resource)

### UI Missing
- Resource allocation UI for mixed choices
- Magic item selection UI on pass (currently uses prompt)
- Discard selection UI for draw_discard effects
- Deck reordering UI for reorder_deck effects

## Implemented

### Core Systems
- Game setup and drafting
- Income phase (fixed and choice income)
- Action phase (play cards, buy monuments/places of power, pass, use abilities)
- Victory check and tie-breakers
- Magic item swap on pass
- First player token mechanics

### Ability System
- Tap costs
- Pay costs (fixed and variable/pay_variable)
- Remove from card costs
- Destroy artifact/self costs
- Discard costs
- Tap another card costs
- Gain effects (fixed, choice, per-opponent)
- Add to card effects
- Attack effects (without reaction pause)
- Draw effects
- Untap effects
- Convert effects (non-gold to gold)
- Passive cost reductions

### Cards
- All artifact costs defined
- All artifact incomes defined (except Vault, Windup Man)
- All artifact abilities defined (execution may vary - see above)
