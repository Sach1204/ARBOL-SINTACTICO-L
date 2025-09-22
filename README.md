# ARBOL-SINTACTICO
# 🌳 Analizador Sintáctico con Árbol de Gramática

Este proyecto implementa un **analizador sintáctico (parser)** que genera y visualiza árboles sintácticos para expresiones matemáticas. El programa incluye un tokenizador manual, un parser recursivo descendente y un sistema de visualización usando NetworkX y Matplotlib.

## Características

- **Tokenizador manual** que reconoce números, identificadores, operadores y paréntesis
- **Parser recursivo descendente** que construye árboles sintácticos
- **Visualización gráfica** de los árboles generados
- **Manejo de precedencia** de operadores (multiplicación antes que suma)
- **Soporte para paréntesis** para modificar la precedencia
- **Interfaz interactiva** de línea de comandos

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
python Arbol.py
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
    # ... procesamiento carácter por carácter
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
tokenize("2+a*3") 
# Resultado: [("num","2"), ("opsuma","+"), ("id","a"), ("opmul","*"), ("num","3"), ("EOF","")]
```

### 2. **Clase Parser**

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0           # posición actual en la lista de tokens
        self.graph = nx.DiGraph()  # grafo dirigido para el árbol
        self.node_id = 0       # contador para IDs únicos de nodos
```

**Métodos auxiliares**:
- `current_token()`: Obtiene el token actual
- `eat(token_type)`: Consume un token esperado y avanza la posición
- `new_node(label)`: Crea un nuevo nodo en el grafo

### 3. **Métodos de Parsing**

#### `parse_E()` - Expresiones
```python
def parse_E(self):
    # E -> E opsuma T | T
    parent = self.new_node("E")
    left = self.parse_T()      # primer término
    self.graph.add_edge(parent, left)
    
    while self.current_token()[0] == "opsuma":  # mientras haya + o -
        op = self.eat("opsuma")
        op_node = self.new_node(op)
        self.graph.add_edge(parent, op_node)
        right = self.parse_T()  # siguiente término
        self.graph.add_edge(parent, right)
    
    return parent
```

**Maneja**: Suma y resta (menor precedencia)

#### `parse_T()` - Términos
```python
def parse_T(self):
    # T -> T opmul F | F
    # Similar a parse_E() pero para multiplicación/división
```

**Maneja**: Multiplicación y división (mayor precedencia)

#### `parse_F()` - Factores
```python
def parse_F(self):
    # F -> id | num | (E)
    parent = self.new_node("F")
    tok_type, _ = self.current_token()
    
    if tok_type == "num":        # número
        val = self.eat("num")
        leaf = self.new_node(val)
        self.graph.add_edge(parent, leaf)
    elif tok_type == "id":       # identificador
        val = self.eat("id")
        leaf = self.new_node(val)
        self.graph.add_edge(parent, leaf)
    elif tok_type == "pari":     # expresión entre paréntesis
        self.eat("pari")
        # ... manejo de paréntesis
```

**Maneja**: Elementos básicos (números, variables, expresiones entre paréntesis)

### 4. **Visualización del Árbol**

#### `hierarchy_pos()` - Cálculo de posiciones
```python
def hierarchy_pos(G, root, width=1.0, vert_gap=0.3, ...):
    # Calcula posiciones jerárquicas para los nodos
    # Distribuye los hijos horizontalmente bajo cada padre
```

**Función**: Organiza los nodos en una estructura de árbol jerárquico.

#### `draw_tree()` - Dibujo del árbol
```python
def draw_tree(graph, root):
    pos = hierarchy_pos(graph, root)  # calcular posiciones
    labels = nx.get_node_attributes(graph, "label")  # obtener etiquetas
    
    plt.figure(figsize=(10, 7))
    nx.draw(graph, pos, with_labels=True, labels=labels, ...)
    plt.savefig("arbol_sintactico.png")
    plt.show()
```

**Función**: Genera la visualización gráfica del árbol sintáctico.

## 📊 Ejemplos

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


### Ejemplo 2: `(a+b)*c`

**Tokens**: `[("pari","("), ("id","a"), ("opsuma","+"), ("id","b"), ("pard",")"), ("opmul","*"), ("id","c"), ("EOF","")]`

**Árbol resultante**:
```
      E
      |
      T
   / | | \
  F  *  F
 /|\    |
( E )   c
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
