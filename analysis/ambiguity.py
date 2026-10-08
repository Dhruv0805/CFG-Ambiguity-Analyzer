from collections import Counter
from typing import List


def analyze_trees(trees, truncated=False):
    return {
        "ambiguous": len(trees) > 1,
        "tree_count": len(trees),
        "truncated": truncated
    }


def _tree_paths(node, path=()):
    result = [(path, node.symbol)]
    for index, child in enumerate(node.children):
        result.extend(_tree_paths(child, path + (index,)))
    return result


def _production(node):
    if not node.children:
        return f"{node.symbol} -> {node.symbol}"
    return f"{node.symbol} -> {' '.join(c.symbol for c in node.children)}"


def diagnose_ambiguity(trees):
    if len(trees) < 2:
        return {
            "summary": "Only one parse tree was found, so no structural ambiguity was observed for this input.",
            "differences": [],
            "shared_root": trees[0].symbol if trees else ""
        }

    a, b = trees[0], trees[1]
    paths_a = dict(_tree_paths(a))
    paths_b = dict(_tree_paths(b))

    differences = []
    all_paths = sorted(set(paths_a) | set(paths_b))

    for path in all_paths:
        sa = paths_a.get(path)
        sb = paths_b.get(path)
        if sa != sb:
            p = ".".join(map(str, path)) if path else "root"
            differences.append(
                f"At node path {p}, Tree 1 uses `{sa}` while Tree 2 uses `{sb}`."
            )

    if _production(a) != _production(b):
        differences.append(
            f"Different root productions: `{_production(a)}` vs `{_production(b)}`."
        )

    # If the path comparison produced nothing, the difference may be a
    # structural re-parenting. Use production sets as a compact signal.
    prod_a = Counter(_production(n) for n in _walk(a))
    prod_b = Counter(_production(n) for n in _walk(b))

    if prod_a != prod_b:
        differences.append("The two trees use different production structures.")

    if not differences:
        differences.append(
            "The alternatives differ in tree structure, but no simple "
            "same-position node difference was isolated."
        )

    return {
        "summary": (
            "The supplied sentence has multiple parse trees. "
            "This means the same token sequence can be derived in more than "
            "one structural way under the supplied CFG."
        ),
        "differences": differences[:12],
        "shared_root": a.symbol
    }


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)
