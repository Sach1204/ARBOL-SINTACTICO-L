import networkx as nx
import matplotlib.pyplot as plt


# === TOKENIZADOR MANUAL ===
def tokenize(expr):
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]

        if c.isdigit():  # número
            num = c
            i += 1
            while i < len(expr) and expr[i].isdigit():
                num += expr[i]
                i += 1
            tokens.append(("num", num))
            continue

        elif c.isalpha():  # identificador
            ident = c
            i += 1
            while i < len(expr) and (expr[i].isalnum() or expr[i] == "_"):
                ident += expr[i]
                i += 1
            tokens.append(("id", ident))
            continue

        elif c in "+-":
            tokens.append(("opsuma", c))

        elif c in "*/":
            tokens.append(("opmul", c))

        elif c == "(":
            tokens.append(("pari", c))

        elif c == ")":
            tokens.append(("pard", c))

        elif c.isspace():
            i += 1
            continue

        else:
            raise ValueError(f"Carácter inesperado: {c}")

        i += 1

    tokens.append(("EOF", ""))
    return tokens


# === PARSER CON ÁRBOL DE GRAMÁTICA ===
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.graph = nx.DiGraph()
        self.node_id = 0

    def current_token(self):
        return self.tokens[self.pos]

    def eat(self, token_type):
        tok_type, tok_val = self.current_token()
        if tok_type == token_type:
            self.pos += 1
            return tok_val
        raise SyntaxError(f"Se esperaba {token_type} pero se encontró {tok_type}")

    def new_node(self, label):
        node = f"{label}_{self.node_id}"
        self.graph.add_node(node, label=label)
        self.node_id += 1
        return node

    # E -> E opsuma T | T
    def parse_E(self):
        parent = self.new_node("E")
        left = self.parse_T()
        self.graph.add_edge(parent, left)
        while self.current_token()[0] == "opsuma":
            op = self.eat("opsuma")
            op_node = self.new_node(op)
            self.graph.add_edge(parent, op_node)
            right = self.parse_T()
            self.graph.add_edge(parent, right)
        return parent

    # T -> T opmul F | F
    def parse_T(self):
        parent = self.new_node("T")
        left = self.parse_F()
        self.graph.add_edge(parent, left)
        while self.current_token()[0] == "opmul":
            op = self.eat("opmul")
            op_node = self.new_node(op)
            self.graph.add_edge(parent, op_node)
            right = self.parse_F()
            self.graph.add_edge(parent, right)
        return parent

    # F -> id | num | (E)
    def parse_F(self):
        parent = self.new_node("F")
        tok_type, _ = self.current_token()
        if tok_type == "num":
            val = self.eat("num")
            leaf = self.new_node(val)
            self.graph.add_edge(parent, leaf)
            return parent
        elif tok_type == "id":
            val = self.eat("id")
            leaf = self.new_node(val)
            self.graph.add_edge(parent, leaf)
            return parent
        elif tok_type == "pari":
            self.eat("pari")
            p_node = self.new_node("(")
            self.graph.add_edge(parent, p_node)
            e_node = self.parse_E()
            self.graph.add_edge(parent, e_node)
            self.eat("pard")
            p_node2 = self.new_node(")")
            self.graph.add_edge(parent, p_node2)
            return parent
        else:
            raise SyntaxError(f"Token inesperado: {tok_type}")

    def parse(self):
        root = self.parse_E()
        if self.current_token()[0] != "EOF":
            raise SyntaxError("Tokens restantes sin usar")
        return root, self.graph


# === DIBUJAR ÁRBOL EN FORMA JERÁRQUICA ===
def hierarchy_pos(G, root, width=1.0, vert_gap=0.3, vert_loc=0, xcenter=0.5, pos=None, parent=None):
    if pos is None:
        pos = {root: (xcenter, vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)

    children = list(G.successors(root))
    if len(children) != 0:
        dx = width / len(children)
        nextx = xcenter - width / 2 - dx / 2
        for child in children:
            nextx += dx
            pos = hierarchy_pos(
                G, child, width=dx, vert_gap=vert_gap,
                vert_loc=vert_loc - vert_gap, xcenter=nextx,
                pos=pos, parent=root,
            )
    return pos


def draw_tree(graph, root):
    pos = hierarchy_pos(graph, root)
    labels = nx.get_node_attributes(graph, "label")

    plt.figure(figsize=(10, 7))
    nx.draw(
        graph,
        pos,
        with_labels=True,
        labels=labels,
        node_size=1200,
        node_color="lightblue",
        font_size=10,
        font_weight="bold",
        arrows=True,
    )
    plt.savefig("arbol_sintactico.png", bbox_inches="tight")
    plt.show()
    print("Arbol sintáctico guardado como 'arbol_sintactico.png'")


# === PROGRAMA PRINCIPAL ===
if __name__ == "__main__":
    print("Ingrese una expresión (ejemplo: 2+3*4 o (a+b)*3). Escriba 'salir' para terminar.\n")

    while True:
        expr = input(">>> ").strip()
        if expr.lower() == "salir":
            print("Saliendo del programa.")
            break
        if expr == "":
            continue
        try:
            tokens = tokenize(expr)
            parser = Parser(tokens)
            root, graph = parser.parse()
            draw_tree(graph, root)
        except Exception as e:
            print("❌ Error:", e)


