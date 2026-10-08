from dataclasses import dataclass, field
from typing import Dict, List, Tuple


class GrammarError(ValueError):
    """Raised when a grammar cannot be parsed."""


@dataclass
class Production:
    lhs: str
    rhs: Tuple[str, ...]


@dataclass
class Grammar:
    productions: Dict[str, List[Tuple[str, ...]]] = field(default_factory=dict)
    start_symbol: str = ""

    @property
    def nonterminals(self):
        return set(self.productions.keys())

    @property
    def rule_count(self):
        return sum(len(v) for v in self.productions.values())

    def pretty(self):
        lines = []
        for lhs, alternatives in self.productions.items():
            rhs = [" ".join(alt) if alt else "ε" for alt in alternatives]
            lines.append(f"{lhs} -> " + " | ".join(rhs))
        return "\n".join(lines)


def _split_rhs(rhs_text: str):
    rhs_text = rhs_text.strip()
    if not rhs_text or rhs_text in {"ε", "epsilon", "EPSILON"}:
        return [tuple()]
    return [tuple(part.strip().split()) for part in rhs_text.split("|")]


def parse_grammar(text: str) -> Grammar:
    productions: Dict[str, List[Tuple[str, ...]]] = {}
    start = ""

    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if "->" not in line:
            raise GrammarError(
                f"Line {line_no}: expected '->' in production."
            )

        lhs, rhs = line.split("->", 1)
        lhs = lhs.strip()

        if not lhs or len(lhs.split()) != 1:
            raise GrammarError(
                f"Line {line_no}: left-hand side must be one symbol."
            )

        if not start:
            start = lhs

        alternatives = _split_rhs(rhs)

        bucket = productions.setdefault(lhs, [])
        for alt in alternatives:
            if alt not in bucket:
                bucket.append(alt)

    if not productions:
        raise GrammarError("The grammar is empty.")

    return Grammar(productions=productions, start_symbol=start)
