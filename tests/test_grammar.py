from parser.grammar_parser import parse_grammar


def test_grammar():
    g = parse_grammar("""
    E -> E + E | id
    """)
    assert g.start_symbol == "E"
    assert g.rule_count == 2
