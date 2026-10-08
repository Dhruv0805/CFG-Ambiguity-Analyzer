import math
import matplotlib.pyplot as plt


def _count_leaves(node):
    if not node.children:
        return 1
    return sum(_count_leaves(c) for c in node.children)


def _depth(node):
    if not node.children:
        return 1
    return 1 + max(_depth(c) for c in node.children)


def render_tree(root):
    """Render a TreeNode as a clean matplotlib diagram."""
    positions = {}
    edges = []
    next_x = [0]

    def assign(node, depth):
        if not node.children:
            x = next_x[0]
            next_x[0] += 1
        else:
            child_xs = [assign(c, depth + 1) for c in node.children]
            x = sum(child_xs) / len(child_xs)

        positions[id(node)] = (x, -depth)
        for child in node.children:
            edges.append((id(node), id(child)))
        return x

    assign(root, 0)

    leaves = max(1, _count_leaves(root))
    depth = _depth(root)

    fig_width = max(8, min(18, leaves * 1.5))
    fig_height = max(4, min(12, depth * 1.2))

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    for parent, child in edges:
        x1, y1 = positions[parent]
        x2, y2 = positions[child]
        ax.plot([x1, x2], [y1, y2], linewidth=1.2)

    def draw_nodes(node):
        x, y = positions[id(node)]
        ax.text(
            x, y, node.symbol,
            ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor="black")
        )
        for child in node.children:
            draw_nodes(child)

    draw_nodes(root)

    ax.set_xlim(-1, max(1, leaves))
    ax.set_ylim(-depth - 1, 1)
    ax.axis("off")
    fig.tight_layout()

    return fig
