# CFG Ambiguity Analyzer & Parse Tree Visualizer

A Python + Streamlit educational project for analyzing **context-free grammar (CFG) ambiguity for a supplied input sentence**.

The project is inspired by the workflow described in *Parse Forest Diagnostics with Dr. Ambiguity*: multiple parse trees are generated, alternatives can be visualized, and their structural differences can be inspected.

## Features

- Enter a custom CFG.
- Enter a tokenized input sentence.
- Parse using an Earley-style chart parser.
- Preserve multiple derivations instead of stopping at the first parse.
- Detect whether the supplied sentence has more than one parse tree.
- Visualize each parse tree.
- Show a basic structural diagnosis between two alternatives.
- Support epsilon productions.
- Bounded maximum-tree setting to prevent runaway output on highly ambiguous grammars.

## Important limitation

Ambiguity of arbitrary CFGs is undecidable in general. Therefore this application should be described as:

> **Sentence-level CFG ambiguity analysis with bounded parse-tree enumeration.**

It does not prove that a grammar is globally ambiguous or globally unambiguous for every possible sentence.

## Grammar syntax

One production per line:

```text
E -> E + E
E -> E * E
E -> ( E )
E -> id
```

Alternatives can also be written on one line:

```text
E -> E + E | E * E | id
```

Epsilon:

```text
A -> ε
```

Comments begin with `#`.

## Tokenization

The input sentence is currently whitespace-tokenized. For example:

```text
id + id * id
```

is treated as:

```text
["id", "+", "id", "*", "id"]
```

## Run locally

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Test

```bash
pytest -q
```

## Example 1: ambiguous

```text
E -> E + E
E -> E * E
E -> ( E )
E -> id
```

Input:

```text
id + id * id
```

The analyzer should find multiple parse trees and report ambiguity.

## Example 2: precedence grammar

```text
E -> E + T
E -> T
T -> T * F
T -> F
F -> ( E )
F -> id
```

Input:

```text
id + id * id
```

The grammar encodes precedence and should produce one parse tree.

## Example 3: dangling else

```text
S -> if E then S
S -> if E then S else S
S -> a
E -> b
```

Input:

```text
if b then if b then a else a
```

This is a useful demonstration of the classic dangling-else ambiguity.

## Project structure

```text
CFG_Ambiguity_Analyzer/
├── app.py
├── parser/
│   ├── __init__.py
│   ├── grammar_parser.py
│   └── earley_parser.py
├── analysis/
│   ├── __init__.py
│   └── ambiguity.py
├── visualization/
│   ├── __init__.py
│   └── tree_visualizer.py
├── examples/
│   ├── ambiguous_arithmetic.txt
│   ├── unambiguous_arithmetic.txt
│   └── dangling_else.txt
├── tests/
│   ├── test_grammar.py
│   └── test_parser.py
├── requirements.txt
└── README.md
```

## Suggested future improvements

- Shared parse-forest visualization.
- Better tree-diff highlighting.
- Automatic minimal ambiguous sentence search.
- FIRST/FOLLOW analysis.
- Grammar validation for unreachable and useless symbols.
- CYK mode for CNF grammars.
- Export parse trees as SVG/PNG.
- Grammar-level ambiguity exploration by bounded sentence generation.
