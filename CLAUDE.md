# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal GitHub Pages site hosting a thesis link, interactive visualizations, and a collection of algorithmic puzzle solutions.

## Running the Code

**Web visualization:**
- Open `centrality/centrality.html` directly in a browser (no build required)

**Python scripts:**
- Run directly with `python <script>.py`
- Scripts use Python 2.7 syntax (print statements, `xrange()`, `raw_input()`)
- Some require data files in the same directory:
  - `Scrabble puzzle/longest_word.py` → needs `scrabble_dict.txt`
  - `hangman/hangman.py` → needs `TWL06.txt`, takes `greedy` or `fair` argument
  - `Song Game/scoreme.py` → needs guess/solution text files

## Architecture

**Frontend (Centrality):**
- HTML5 Canvas visualization comparing mean vs median
- jQuery 1.6 for DOM manipulation
- Interactive: double-click to add points, drag to reposition

**Python Puzzles:**
- Standalone algorithm implementations (no shared dependencies)
- Game theory solvers: `538 Puzzle.py`, `hats.py`
- Word/language puzzles: `longest_word.py`, `Ghost Solver.py`, `hangman.py`
- Probability simulation: `ring_attack.py` (uses NumPy)
- Scoring: `scoreme.py` calculates Kendall distance for ranking comparison

## Res Arcana (in development)

Browser-based implementation of the board game Res Arcana.

**Architecture:** Python/Flask backend (game state/logic) + JavaScript frontend (rendering)

**Virtual environment:** `~/venvs/general` (has Flask installed)

**To run the server:**
```bash
~/venvs/general/bin/python "Res Arcana/server.py"
```
Then open http://localhost:5001 in a browser.

**Current status:** Draft phase, income phase, action phase with card abilities implemented. Bot players for testing.

**Files:**
- `game_state.py` - Python data structures for game state
- `game_logic.py` - Game rules and ability system
- `cards.py` - Card definitions with costs, income, and abilities
- `server.py` - Flask server with API endpoints
- `index.html`, `style.css`, `renderer.js` - Frontend rendering
- `tests/` - Python test files

**Running tests:**
```bash
cd "Res Arcana/tests"
~/venvs/general/bin/python test_game_loop.py
~/venvs/general/bin/python test_abilities.py
```

**Implementation guidelines:**
- Do NOT "simplify" card implementations or deviate from the specified behavior without explicitly informing the user. If a card's effect is too complex to implement with current infrastructure, say "this card has not been implemented yet" rather than implementing a simplified version that introduces known bugs.
- When implementing cards, verify the implementation matches the comment/description exactly before considering it done.
