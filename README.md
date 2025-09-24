# ARBOL-SINTACTICO
# Analizador Sintáctico con Árbol de Gramática

Este proyecto implementa un **analizador sintáctico (parser)** que genera y visualiza árboles sintácticos para expresiones matemáticas. El programa incluye un tokenizador manual, un parser recursivo descendente y un sistema de visualización usando NetworkX y Matplotlib.

## Gramática Soportada

El analizador implementa la siguiente gramática libre de contexto:

```
E -> E opsuma T | T
T -> T opmul F | F
F -> id | num | (E)

Donde:
- E = Expresión
- T = Término
- F = Factor
- opsuma = + | -
- opmul = * | /
- id = identificador (variables como 'a', 'x', 'variable_1')
- num = número entero
- pari = (
- pard = )
```

Esta gramática asegura que:
- La **multiplicación y división** tienen mayor precedencia que la **suma y resta**
- Los **paréntesis** pueden modificar el orden de evaluación
- Se pueden usar tanto **números** como **identificadores** (variables)

## Instalación

### Requisitos

```bash
pip install networkx matplotlib
```
## Uso

Ejecuta el programa y ingresa expresiones matemáticas:

```bash
python3 Arbol.py
```

```
Ingrese una expresión (ejemplo: 2+3*4 o (a+b)*3). Escriba 'salir' para terminar.

>>> 2+3*4
>>> (a+b)*c
>>> x*y+z
>>> salir
```

Para cada expresión válida, el programa:
1. Genera el árbol sintáctico
2. Muestra la visualización gráfica
3. Guarda la imagen como `arbol_sintactico.png`

## Explicación del Código

### 1. **Tokenizador Manual** (`tokenize`)

```python
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

```

**Función**: Convierte una cadena de texto en una lista de tokens (unidades léxicas).

**Tokens reconocidos**:
- `("num", "123")` - números enteros
- `("id", "variable")` - identificadores (variables)
- `("opsuma", "+")` - operadores de suma/resta
- `("opmul", "*")` - operadores de multiplicación/división
- `("pari", "(")` - paréntesis izquierdo
- `("pard", ")")` - paréntesis derecho
- `("EOF", "")` - final de la expresión

**Ejemplo**:
```python
tokenize("2+3*4") 
# Resultado: [("num","2"), ("opsuma","+"), ("id","3"), ("opmul","*"), ("num","4"), ("EOF","")]
```

### 2. **Clase Parser**

```python
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
```

**Métodos auxiliares**:
- `current_token()`: Obtiene el token actual
- `eat(token_type)`: Consume un token esperado y avanza la posición
- `new_node(label)`: Crea un nuevo nodo en el grafo

### 3. **Métodos de Parsing**

#### `parse_E()` - Expresiones
```python
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
```

**Maneja**: Suma y resta (menor precedencia)

#### `parse_T()` - Términos
```python
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

```

**Maneja**: Multiplicación y división (mayor precedencia)

#### `parse_F()` - Factores
```python
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
```

**Maneja**: Elementos básicos (números, variables, expresiones entre paréntesis)

### 4. **Visualización del Árbol**

#### `hierarchy_pos()` - Cálculo de posiciones
```python
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

```

**Función**: Organiza los nodos en una estructura de árbol jerárquico.

#### `draw_tree()` - Dibujo del árbol
```python
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
```

**Función**: Genera la visualización gráfica del árbol sintáctico.

## Ejemplos

### Ejemplo 1: `2+3*4`

**Tokens**: `[("num","2"), ("opsuma","+"), ("num","3"), ("opmul","*"), ("num","4"), ("EOF","")]`

**Árbol resultante**:
```
     E
   / | \
  T  +  T
  |    / | \
  F   F  *  F
  |   |     |
  2   3     4
```
**Como se ve en terminal**
<img width="1018" height="148" alt="image" src="https://github.com/user-attachments/assets/5c6e4a00-467b-498a-b745-94b9ca5eda2b" />

**Como se ve al ser creado**
<img width="1018" height="774" alt="image" src="https://github.com/user-attachments/assets/0175e514-ad97-4d63-ae09-013a9b13b1f4" />


### Ejemplo 2: `(a+b)*3`

**Tokens**: `[("pari","("), ("id","a"), ("opsuma","+"), ("id","b"), ("pard",")"), ("opmul","*"), ("id","3"), ("EOF","")]`

**Árbol resultante**:
```
      E
      |
      T
   / | | \
  F  *  F
 /|\    |
( E )   3
 /|\
T + T
|   |
F   F
|   |
a   b
```
**Como se ve en terminal**
<img width="1018" height="95" alt="image" src="https://github.com/user-attachments/assets/934e1c20-99b5-4f5c-8d06-138a9c253250" />


**Como se ve al ser creado**
<img width="1018" height="792" alt="image" src="https://github.com/user-attachments/assets/d6730b6d-e0c5-49df-a44d-8b6b6aa6b6c5" />
