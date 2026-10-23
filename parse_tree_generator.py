"""
Parse Tree Generator - Context-Free Grammar (CFG)
Python 3 + Tkinter (no external packages required).

Grammar format:
    S -> aSb | ε
    S -> aA | b
Use one production per line; alternatives may be separated by |.
Nonterminals are single uppercase letters (A-Z). Other characters are terminals.
Use ε, epsilon, or an empty alternative for the empty string.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque

EPSILON_WORDS = {"ε", "epsilon", "eps", "λ", "lambda"}


def parse_grammar(text):
    grammar = {}
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "->" not in line:
            raise ValueError(f"Line {line_no}: use the format A -> production.")
        lhs, rhs_text = line.split("->", 1)
        lhs = lhs.strip()
        if len(lhs) != 1 or not lhs.isupper() or not lhs.isalpha():
            raise ValueError(f"Line {line_no}: the left side must be one uppercase letter, e.g. S.")
        alternatives = rhs_text.split("|")
        grammar.setdefault(lhs, [])
        for alt in alternatives:
            alt = alt.strip()
            if alt.lower() in EPSILON_WORDS or alt == "":
                alt = ""
            if any(ch.isspace() for ch in alt):
                raise ValueError(
                    f"Line {line_no}: write each production without spaces inside it. "
                    "This version uses single-character grammar symbols."
                )
            grammar[lhs].append(alt)
    if not grammar:
        raise ValueError("Enter at least one production.")
    for lhs, alternatives in grammar.items():
        for rhs in alternatives:
            for ch in rhs:
                if ch.isupper() and ch.isalpha() and ch not in grammar:
                    raise ValueError(f"Nonterminal {ch} is used but has no production.")
    return grammar


def nonterminals_in(form, grammar):
    return [i for i, ch in enumerate(form) if ch in grammar]


def can_still_match(form, target, grammar):
    """Prune a sentential form if its existing terminal prefix/suffix conflicts."""
    terminal_prefix = ""
    for ch in form:
        if ch in grammar:
            break
        terminal_prefix += ch
    if not target.startswith(terminal_prefix):
        return False

    terminal_suffix = ""
    for ch in reversed(form):
        if ch in grammar:
            break
        terminal_suffix = ch + terminal_suffix
    if not target.endswith(terminal_suffix):
        return False

    # A derivation cannot shrink below the number of already-present terminals.
    terminal_count = sum(1 for ch in form if ch not in grammar)
    return terminal_count <= len(target)


def find_derivation(grammar, start, target, mode, max_states=100000):
    """Breadth-first search for a leftmost or rightmost derivation."""
    queue = deque([(start, [start])])
    seen = {start}
    states = 0
    max_steps = max(20, len(target) * 4 + len(grammar) * 6 + 10)

    while queue and states < max_states:
        form, path = queue.popleft()
        states += 1

        if not any(ch in grammar for ch in form):
            if form == target:
                return path
            continue
        if len(path) > max_steps:
            continue

        positions = nonterminals_in(form, grammar)
        if not positions:
            continue
        index = positions[0] if mode == "leftmost" else positions[-1]
        symbol = form[index]

        for rhs in grammar[symbol]:
            next_form = form[:index] + rhs + form[index + 1:]
            if len(next_form) > len(target) + 2 * len(grammar) + 8:
                continue
            if not can_still_match(next_form, target, grammar):
                continue
            if next_form not in seen:
                seen.add(next_form)
                queue.append((next_form, path + [next_form]))

    return None


def tree_from_derivation(grammar, path):
    """Reconstruct a parse tree by applying each derivation step to its expanded leaf."""
    root = {"label": path[0], "children": []}
    frontier_nodes = [root]  # one node per symbol in the current sentential form

    for previous, current in zip(path, path[1:]):
        changed = None
        for index, symbol in enumerate(previous):
            if symbol not in grammar:
                continue
            for rhs in grammar[symbol]:
                if previous[:index] + rhs + previous[index + 1:] == current:
                    changed = (index, symbol, rhs)
                    break
            if changed:
                break
        if not changed:
            raise ValueError("Could not reconstruct parse tree from derivation.")
        index, symbol, rhs = changed
        node = frontier_nodes[index]
        children = [{"label": ch, "children": []} for ch in rhs]
        if not rhs:
            children = [{"label": "ε", "children": [], "epsilon_leaf": True}]
        node["children"] = children
        # Epsilon is shown in the tree, but it is not a symbol in the sentential form.
        frontier_nodes[index:index + 1] = ([child for child in children if not child.get("epsilon_leaf")] if not rhs else children)
    return root


def format_tree(root):
    lines = []
    def visit(node, prefix="", last=True, is_root=True):
        label = node["label"]
        if is_root:
            lines.append(label)
        else:
            lines.append(prefix + ("└── " if last else "├── ") + label)
        children = node.get("children", [])
        next_prefix = prefix if is_root else prefix + ("    " if last else "│   ")
        for i, child in enumerate(children):
            visit(child, next_prefix, i == len(children) - 1, False)
    visit(root)
    return "\n".join(lines)


def render_tree(canvas, root):
    canvas.delete("all")
    canvas.update_idletasks()
    width = max(canvas.winfo_width(), 600)
    x_gap, y_gap = 74, 70
    nodes = []
    edges = []

    def layout(node, depth=0):
        children = node.get("children", [])
        if not children:
            x = len(nodes) * x_gap + 40
            nodes.append((node, x, depth * y_gap + 35))
            return x
        child_xs = [layout(child, depth + 1) for child in children]
        x = sum(child_xs) / len(child_xs)
        nodes.append((node, x, depth * y_gap + 35))
        for child, cx in zip(children, child_xs):
            edges.append((x, depth * y_gap + 35, cx, (depth + 1) * y_gap + 35))
        return x

    layout(root)
    if nodes:
        min_x = min(x for _, x, _ in nodes)
        max_x = max(x for _, x, _ in nodes)
        content_width = max_x - min_x + 100
        offset = max(20, (width - content_width) / 2) - min_x
        for x1, y1, x2, y2 in edges:
            canvas.create_line(x1 + offset, y1 + 18, x2 + offset, y2 - 18, width=1.5)
        for node, x, y in nodes:
            x += offset
            label = node["label"]
            canvas.create_oval(x - 22, y - 18, x + 22, y + 18, fill="#eee8ff", outline="#5b3b9e", width=1.5)
            canvas.create_text(x, y, text=label, font=("Arial", 11, "bold"))
        canvas.configure(scrollregion=(0, 0, max(width, content_width + 30), max(y for _, _, y in nodes) + 70))


class ParseTreeApp:
    def __init__(self, root):
        self.root = root
        root.title("CFG Parse Tree Generator")
        root.geometry("1050x800")
        root.minsize(850, 650)

        heading = ttk.Label(root, text="Parse Tree Generator", font=("Arial", 19, "bold"))
        heading.pack(pady=(12, 4))
        ttk.Label(
            root,
            text="Enter one-character grammar symbols. Uppercase letters are nonterminals; other characters are terminals.",
            wraplength=950
        ).pack(pady=(0, 10))

        input_frame = ttk.Frame(root, padding=10)
        input_frame.pack(fill="x")
        ttk.Label(input_frame, text="CFG productions (one rule per line):").grid(row=0, column=0, sticky="w")
        self.grammar_box = tk.Text(input_frame, height=5, width=52, font=("Consolas", 11))
        self.grammar_box.grid(row=1, column=0, rowspan=3, sticky="nsew", padx=(0, 20), pady=5)
        self.grammar_box.insert("1.0", "S -> aSb | ε")

        ttk.Label(input_frame, text="Start symbol:").grid(row=0, column=1, sticky="w")
        self.start_entry = ttk.Entry(input_frame, width=12)
        self.start_entry.grid(row=1, column=1, sticky="w", pady=5)
        self.start_entry.insert(0, "S")

        ttk.Label(input_frame, text="Input string:").grid(row=2, column=1, sticky="w")
        self.string_entry = ttk.Entry(input_frame, width=24)
        self.string_entry.grid(row=3, column=1, sticky="w", pady=5)
        self.string_entry.insert(0, "aabb")

        ttk.Button(input_frame, text="Generate", command=self.generate).grid(row=4, column=1, sticky="w", pady=8)
        ttk.Button(input_frame, text="Load example", command=self.load_example).grid(row=4, column=0, sticky="w", pady=8)
        input_frame.columnconfigure(0, weight=1)

        self.status = ttk.Label(root, text="Ready. Click Generate to test the input.", font=("Arial", 11, "bold"))
        self.status.pack(anchor="w", padx=15, pady=(0, 8))

        output = ttk.Panedwindow(root, orient="horizontal")
        output.pack(fill="both", expand=True, padx=10, pady=5)

        left = ttk.Frame(output, padding=5)
        right = ttk.Frame(output, padding=5)
        output.add(left, weight=1)
        output.add(right, weight=1)

        ttk.Label(left, text="Derivations", font=("Arial", 13, "bold")).pack(anchor="w")
        self.result_box = tk.Text(left, wrap="word", font=("Consolas", 10), width=45)
        self.result_box.pack(fill="both", expand=True, pady=5)
        self.result_box.configure(state="disabled")

        ttk.Label(right, text="Parse tree", font=("Arial", 13, "bold")).pack(anchor="w")
        self.tree_canvas = tk.Canvas(right, background="white", height=400, scrollregion=(0, 0, 1200, 800))
        xscroll = ttk.Scrollbar(right, orient="horizontal", command=self.tree_canvas.xview)
        yscroll = ttk.Scrollbar(right, orient="vertical", command=self.tree_canvas.yview)
        self.tree_canvas.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        self.tree_canvas.pack(side="top", fill="both", expand=True)
        xscroll.pack(side="bottom", fill="x")
        yscroll.pack(side="right", fill="y")

        ttk.Label(
            root,
            text="Tip: use ε for the empty string. Example grammar: S -> aSb | ε; input: aabb.",
            foreground="#555"
        ).pack(pady=8)

    def load_example(self):
        self.grammar_box.delete("1.0", "end")
        self.grammar_box.insert("1.0", "S -> aSb | ε")
        self.start_entry.delete(0, "end")
        self.start_entry.insert(0, "S")
        self.string_entry.delete(0, "end")
        self.string_entry.insert(0, "aabb")

    def set_output(self, text):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", text)
        self.result_box.configure(state="disabled")

    def generate(self):
        try:
            grammar = parse_grammar(self.grammar_box.get("1.0", "end"))
            start = self.start_entry.get().strip()
            target = self.string_entry.get()
            if len(start) != 1 or start not in grammar:
                raise ValueError("The start symbol must be one uppercase nonterminal defined in the grammar.")

            left_path = find_derivation(grammar, start, target, "leftmost")
            right_path = find_derivation(grammar, start, target, "rightmost")

            if left_path is None or right_path is None:
                self.status.configure(text=f"REJECTED: '{target}' is not generated (or search limit reached).", foreground="red")
                self.set_output(
                    f"Input string: {target!r}\n"
                    f"Membership: REJECTED\n\n"
                    f"No derivation was found within the search limits.\n"
                    f"Check the grammar, start symbol, and input string."
                )
                self.tree_canvas.delete("all")
                return

            tree = tree_from_derivation(grammar, left_path)
            left_text = " ⇒ ".join(form if form else "ε" for form in left_path)
            right_text = " ⇒ ".join(form if form else "ε" for form in right_path)
            result = (
                f"Input string: {target!r}\n"
                f"Membership: ACCEPTED\n\n"
                f"LEFTMOST DERIVATION\n{left_text}\n\n"
                f"RIGHTMOST DERIVATION\n{right_text}\n\n"
                f"PARSE TREE (text view)\n{format_tree(tree)}\n\n"
                f"Note: for an empty input string, use a blank input field."
            )
            self.status.configure(text=f"ACCEPTED: '{target}' belongs to the grammar's language.", foreground="green")
            self.set_output(result)
            render_tree(self.tree_canvas, tree)
        except Exception as exc:
            messagebox.showerror("Input error", str(exc))


def main():
    root = tk.Tk()
    ParseTreeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
