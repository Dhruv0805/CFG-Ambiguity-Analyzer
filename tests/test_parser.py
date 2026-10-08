from parser.grammar_parser import parse_grammar
from parser.earley_parser import parse_input


def test_unambiguous():
    g = parse_grammar("""
    E -> E + T
    E -> T
    T -> id
    """)
    r = parse_input(g, "id + id")
    assert r.accepted
    assert len(r.trees) == 1


def test_ambiguous():
    g = parse_grammar("""
    E -> E + E
    E -> id
    """)
    r = parse_input(g, "id + id + id", max_trees=10)
    assert r.accepted
    assert len(r.trees) >= 2
