from dataclasses import dataclass
from typing import Dict, List, Tuple, Set

from .grammar_parser import Grammar


@dataclass(frozen=True)
class TreeNode:
    symbol: str
    children: Tuple["TreeNode", ...] = tuple()

    def to_text(self, level=0):
        indent = "  " * level
        if not self.children:
            return f"{indent}{self.symbol}"
        lines = [f"{indent}{self.symbol}"]
        for child in self.children:
            lines.append(child.to_text(level + 1))
        return "\n".join(lines)


@dataclass
class ParseResult:
    accepted: bool
    trees: List[TreeNode]
    token_count: int
    truncated: bool = False
    message: str = ""


@dataclass(frozen=True)
class Core:
    lhs: str
    rhs: Tuple[str, ...]
    dot: int
    start: int


class State:
    __slots__ = ("core", "children")

    def __init__(self, core: Core, children=()):
        self.core = core
        self.children = tuple(children)


def _tokenize(sentence: str):
    return sentence.strip().split() if sentence.strip() else []


def parse_input(grammar: Grammar, sentence: str, max_trees=10) -> ParseResult:
    tokens = _tokenize(sentence)
    n = len(tokens)
    start = grammar.start_symbol

    # Augmented grammar symbol is deliberately outside user grammar.
    augmented = "__START__"
    while augmented in grammar.nonterminals:
        augmented += "_"

    charts: List[Dict[Core, List[Tuple[TreeNode, ...]]]] = [
        {} for _ in range(n + 1)
    ]

    root_core = Core(augmented, (start,), 0, 0)
    charts[0][root_core] = [tuple()]

    truncated = False

    def add(chart_index, core, children):
        nonlocal truncated
        bucket = charts[chart_index].setdefault(core, [])
        children = tuple(children)
        if children in bucket:
            return False
        if len(bucket) >= max_trees:
            truncated = True
            return False
        bucket.append(children)
        return True

    # Earley chart construction. Each state core can hold several
    # child-sequences, allowing us to preserve alternative derivations.
    for i in range(n + 1):
        changed = True
        while changed:
            changed = False

            # Snapshot is important because completion can add states while
            # this chart is being saturated.
            items = list(charts[i].items())

            for core, derivations in items:
                if core.dot < len(core.rhs):
                    symbol = core.rhs[core.dot]

                    # Prediction
                    if symbol in grammar.nonterminals:
                        for rhs in grammar.productions[symbol]:
                            new_core = Core(symbol, rhs, 0, i)
                            if add(i, new_core, ()):
                                changed = True

                    # Scanning
                    elif i < n and symbol == tokens[i]:
                        new_core = Core(
                            core.lhs, core.rhs, core.dot + 1, core.start
                        )
                        for children in derivations:
                            child = TreeNode(symbol)
                            if add(i + 1, new_core, children + (child,)):
                                # Scans are processed in the next chart,
                                # so no need to mark this chart as changed.
                                pass

                else:
                    # Completion
                    if core.lhs == augmented and core.start == 0:
                        continue

                    completed = TreeNode(core.lhs, tuple(
                        child for child in derivations[0]
                    ))

                    parent_items = list(charts[core.start].items())
                    for parent_core, parent_derivations in parent_items:
                        if parent_core.dot >= len(parent_core.rhs):
                            continue
                        if parent_core.rhs[parent_core.dot] != core.lhs:
                            continue

                        advanced = Core(
                            parent_core.lhs,
                            parent_core.rhs,
                            parent_core.dot + 1,
                            parent_core.start
                        )

                        for parent_children in parent_derivations:
                            # Each derivation of the completed state must be
                            # paired with each derivation of the parent.
                            for completed_children in derivations:
                                completed_node = TreeNode(
                                    core.lhs, tuple(completed_children)
                                )
                                if add(
                                    i,
                                    advanced,
                                    parent_children + (completed_node,)
                                ):
                                    changed = True

    final_core = Core(augmented, (start,), 1, 0)
    trees = []

    for children in charts[n].get(final_core, []):
        if children and children[0].symbol == start:
            trees.append(children[0])

    # Remove exact duplicates while preserving order.
    unique = []
    seen = set()
    for tree in trees:
        key = tree.to_text()
        if key not in seen:
            seen.add(key)
            unique.append(tree)

    if not unique:
        return ParseResult(
            accepted=False,
            trees=[],
            token_count=n,
            truncated=truncated,
            message="No complete parse was found."
        )

    return ParseResult(
        accepted=True,
        trees=unique[:max_trees],
        token_count=n,
        truncated=truncated or len(unique) > max_trees,
        message="Parse completed successfully."
    )
