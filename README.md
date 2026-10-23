# Parse Tree Generator (CFG)

## Requirements
- Python 3.8 or newer
- Tkinter (included with most standard Python installations)
- No pip packages are required.

## Run
1. Save/extract `parse_tree_generator.py`.
2. Open a terminal or Command Prompt in that folder.
3. Run: `python parse_tree_generator.py`
4. Enter the grammar, start symbol, and input string.
5. Click **Generate**.

## Grammar format
- One production per line, e.g. `S -> aSb`
- Use `|` for alternatives, e.g. `S -> aSb | ε`
- Nonterminals are single uppercase letters (A-Z).
- All other characters are terminals.
- Use `ε` (or `epsilon`) for the empty string.
- Do not put spaces inside a production.

## Demonstration
Grammar:
    S -> aSb | ε
Start symbol: S
Input: aabb

Expected:
- Membership: ACCEPTED
- Leftmost derivation: S ⇒ aSb ⇒ aaSbb ⇒ aabb
- Rightmost derivation: S ⇒ aSb ⇒ aaSbb ⇒ aabb
- A parse tree is drawn in the application.

Try input `aab` to demonstrate rejection.

## Scope and limitations
This educational implementation uses single-character grammar symbols and bounded breadth-first search. It is designed for small classroom examples, not as a production parser for every possible CFG. Highly ambiguous or difficult left-recursive grammars may require more search time or a more advanced parsing algorithm.
