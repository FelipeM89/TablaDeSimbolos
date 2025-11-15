# Tabla de Símbolos y ETDS con Código de Tres Direcciones
---
## **Requisitos de la Tarea**

 1. Escoger una gramática → Gramática de expresiones aritméticas con declaraciones
 2. Hacer un ETDS → Implementado con atributos sintetizados e heredados
 3. Tabla de símbolos → Gestión completa con alcances y validación semántica
 4. Código de tres direcciones → Representación del AST decorado (AST_D)
---
## **Gramática Seleccionada**

```
S  → D S | E
D  → int id ; | float id ;
E  → E + T | E - T | T
T  → T * F | T / F | F
F  → ( E ) | num | id
```
**Características:**

- Soporta declaraciones de variables (int, float)
- Operadores aritméticos: +, -, *, /
- Precedencia: ( ) > * / > + -
- Asociatividad izquierda

## **Esquema de Traducción Dirigida por Sintaxis (ETDS)**
Definición de Atributos

**Atributos Sintetizados**

 No Terminal | Atributo   | Tipo     | Descripción                                  |
|-------------|------------|----------|----------------------------------------------|
| **E, T, F** | `val`      | numérico | Valor calculado de la expresión.             |
| **E, T, F** | `tipo`     | string   | Tipo de dato (`int` o `float`).              |
| **E, T, F** | `lugar`    | string   | Variable temporal que almacena el resultado. |
| **E, T, F** | `codigo`   | string   | Código intermedio generado.                  |
| **D**       | `nombre`   | string   | Nombre de la variable declarada.             |
| **D**       | `tipo_var` | string   | Tipo de la variable (`int` o `float`).       |

**Atributos Heredados**

| No Terminal | Atributo | Descripción                               |
|-------------|----------|-------------------------------------------|
| **E, T, F** | `tabla`  | Referencia a la tabla de símbolos activa. |
| **E, T, F** | `linea`  | Número de línea en el código fuente.      |

---

## **Reglas Semánticas del ETDS**

**Declaración de Variables**
```
D → tipo id ;
{
    D.tipo_var = tipo.lexema
    D.nombre = id.lexema
    
    // Validación semántica
    if existe_en_alcance_actual(id.lexema) then
        error("Variable ya declarada")
    else
        insertar_en_tabla(id.lexema, tipo.lexema, linea_actual)
    
    // Código intermedio
    D.codigo = "declare " || id.lexema || " : " || tipo.lexema
}
```
**Expresión con Suma**
```
E → E₁ + T
{
    // Coerción de tipos
    E.tipo = coercion(E₁.tipo, T.tipo)
    
    // Evaluación de valor (si es constante)
    if E₁.val ≠ null and T.val ≠ null then
        E.val = E₁.val + T.val
    
    // Generación de código intermedio
    temp = nuevo_temporal()
    E.lugar = temp
    E.codigo = E₁.codigo || T.codigo || 
               temp || " = " || E₁.lugar || " + " || T.lugar
}
```
**Expresión con Resta**
```
E → E₁ - T
{
    E.tipo = coercion(E₁.tipo, T.tipo)
    if E₁.val ≠ null and T.val ≠ null then
        E.val = E₁.val - T.val
    
    temp = nuevo_temporal()
    E.lugar = temp
    E.codigo = E₁.codigo || T.codigo || 
               temp || " = " || E₁.lugar || " - " || T.lugar
}
```
**Término con Multiplicación**
```
T → T₁ * F
{
    T.tipo = coercion(T₁.tipo, F.tipo)
    if T₁.val ≠ null and F.val ≠ null then
        T.val = T₁.val * F.val
    
    temp = nuevo_temporal()
    T.lugar = temp
    T.codigo = T₁.codigo || F.codigo || 
               temp || " = " || T₁.lugar || " * " || F.lugar
}
```
**Término con División**
```
T → T₁ / F
{
    // Validación de división por cero
    if F.val = 0 then
        error("División por cero")
    
    T.tipo = coercion(T₁.tipo, F.tipo)
    if T₁.val ≠ null and F.val ≠ null then
        T.val = T₁.val / F.val
    
    temp = nuevo_temporal()
    T.lugar = temp
    T.codigo = T₁.codigo || F.codigo || 
               temp || " = " || T₁.lugar || " / " || F.lugar
}
```
**Factor: Número Litera**
```
F → num
{
    // Determinar tipo según formato
    if "." in num.lexema then
        F.tipo = 'float'
    else
        F.tipo = 'int'
    
    F.val = convertir(num.lexema)
    F.lugar = num.lexema
    F.codigo = ""  // Los literales no generan código
}
```
**Factor: Identificador**
```
F → id
{
    // Validación semántica
    if not existe_en_tabla(id.lexema) then
        error("Variable no declarada: " || id.lexema)
    
    // Obtener información de la tabla de símbolos
    F.tipo = obtener_tipo(id.lexema)
    F.val = obtener_valor(id.lexema)
    F.lugar = id.lexema
    F.codigo = ""
    
    // Marcar variable como usada
    marcar_usado(id.lexema)
}
```
**Factor: Expresión entre Paréntesis**

```
F → ( E )
{
    // Los atributos se heredan directamente de E
    F.tipo = E.tipo
    F.val = E.val
    F.lugar = E.lugar
    F.codigo = E.codigo
}
```
**Función de Coerción de Tipos**
```
  def coercion(tipo1, tipo2):
    """
    Reglas de coerción implícita:
    - int ⊕ int → int
    - int ⊕ float → float
    - float ⊕ int → float
    - float ⊕ float → float
    """
    if tipo1 == 'float' or tipo2 == 'float':
        return 'float'
    return 'int'
```
---
## **Tabla De Simbolos**

Estructura de Datos

```py
class Simbolo:
    nombre: str       # Identificador de la variable
    tipo: str         # 'int' o 'float'
    alcance: int      # Nivel de anidamiento (0 = global)
    linea: int        # Línea de declaración
    valor: any        # Último valor asignado
    usado: bool       # Si la variable fue referenciada
```
Operaciones Implementadas

| Operación                         | Descripción                                   | Complejidad |
|-----------------------------------|-----------------------------------------------|-------------|
| `insertar(nombre, tipo, linea)`   | Agrega un símbolo al alcance actual.          | O(1)        |
| `buscar(nombre)`                  | Busca un símbolo en los alcances visibles.    | O(n)        |
| `existe(nombre)`                  | Verifica si el símbolo existe.                | O(n)        |
| `validar_declaracion(nombre, linea)` | Valida el uso de una variable.             | O(n)        |
| `obtener_tipo(nombre)`            | Retorna el tipo de la variable.               | O(n)        |
| `actualizar_valor(nombre, valor)` | Actualiza el valor asignado a una variable.   | O(n)        |
| `marcar_usado(nombre)`            | Marca una variable como usada.                | O(n)        |
| `entrar_alcance()`                | Crea un nuevo nivel de alcance.               | O(1)        |
| `salir_alcance()`                 | Elimina un alcance y detecta variables no usadas. | O(m)    |

Donde: n = número de alcances, m = símbolos en el alcance
**Ejemplo de Tabla de Símbolos**
Código fuente:
```py
int x;
float y;
int z;
x = 5 + 3 * 2;
y = x / 2.0;
```
Tabla de símbolos generada:
```
================================================================================
                           TABLA DE SÍMBOLOS                           
================================================================================
Nombre     Tipo     Alcance  Línea  Valor      Usado
--------------------------------------------------------------------------------
x          int      0        1      11         Sí   
y          float    0        2      5.5        Sí   
z          int      0        3      None       No   
================================================================================
```
Análisis:

x y y fueron usadas → ✅ Sin advertencias
z fue declarada pero nunca usada → ⚠️ Warning

**Errores Semánticos Detectados**
1. Variable No Declarada
```py
int x;
y = x + 5;  // ❌ Error: Variable 'y' no declarada
```
2. Redeclaración de Variable
```
int x;
float x;    // ❌ Error: Variable 'x' ya declarada en línea 1
```
3. División por Cero
```
int x;
x = 10 / 0; // ❌ Error: División por cero detectada
```
4. Variable No Usada (Warning)
```
int x;
int y;      // ⚠️ Warning: Variable 'y' declarada pero no usada
x = 5;
```
---

## **Código de Tres Direcciones (AST_D)**

Formato
El código intermedio generado sigue el formato de 3 direcciones:
```
destino = operando1 op operando2
```
Donde:

- destino: Variable (normal o temporal)
- operando1, operando2: Variables, temporales o constantes
- op: Operador aritmético (+, -, *, /)

## Representación del AST Decorado (AST_D)
El código de tres direcciones representa el AST decorado de forma lineal, preservando:
- El orden de evaluación
- La precedencia de operadores
- Los valores temporales
- Las asignaciones a variables
---
## Ejemplo Completo

Entrada:
```py
int x;
int y;
float resultado;
x = 5 + 3 * 2;
y = x - 1;
resultado = x / 2.0 + y;
```
AST Decorado (representación visual):
```
Programa [tipo: void]
├── Declaracion [tipo: void]
│   ├── int
│   └── x [tipo: int]
├── Declaracion [tipo: void]
│   ├── int
│   └── y [tipo: int]
├── Declaracion [tipo: void]
│   ├── float
│   └── resultado [tipo: float]
├── Asignacion [tipo: int, val: 11]
│   ├── x [tipo: int]
│   └── + [tipo: int, val: 11, lugar: t2]
│       ├── 5 [tipo: int, val: 5]
│       └── * [tipo: int, val: 6, lugar: t1]
│           ├── 3 [tipo: int, val: 3]
│           └── 2 [tipo: int, val: 2]
├── Asignacion [tipo: int, val: 10]
│   ├── y [tipo: int]
│   └── - [tipo: int, val: 10, lugar: t3]
│       ├── x [tipo: int, val: 11]
│       └── 1 [tipo: int, val: 1]
└── Asignacion [tipo: float, val: 15.5]
    ├── resultado [tipo: float]
    └── + [tipo: float, val: 15.5, lugar: t5]
        ├── / [tipo: float, val: 5.5, lugar: t4]
        │   ├── x [tipo: int, val: 11]
        │   └── 2.0 [tipo: float, val: 2.0]
        └── y [tipo: int, val: 10]
```
Código de Tres Direcciones (AST_D):
```
declare x : int
declare y : int
declare resultado : float
t1 = 3 * 2
t2 = 5 + t1
x = t2
t3 = x - 1
y = t3
t4 = x / 2.0
t5 = t4 + y
resultado = t5
```
**Análisis del Código Generado:**
| Línea                      | Descripción          | Observación                          |
|----------------------------|----------------------|---------------------------------------|
| `declare x : int`          | Declaración de `x`   | Reserva espacio en memoria            |
| `declare y : int`          | Declaración de `y`   | Tipo entero                           |
| `declare resultado : float`| Declaración de `resultado` | Tipo flotante                    |
| `t1 = 3 * 2`               | Evalúa `3 * 2`       | `t1 = 6` (precedencia)                |
| `t2 = 5 + t1`              | Evalúa `5 + 6`       | `t2 = 11`                              |
| `x = t2`                   | Asigna a `x`         | `x = 11`                               |
| `t3 = x - 1`               | Evalúa `x - 1`       | `t3 = 10`                              |
| `y = t3`                   | Asigna a `y`         | `y = 10`                               |
| `t4 = x / 2.0`             | Evalúa `x / 2.0`     | `t4 = 5.5` (coerción a float)          |
| `t5 = t4 + y`              | Evalúa `5.5 + 10`    | `t5 = 15.5` (coerción a float)         |
| `resultado = t5`           | Asigna `resultado`   | `resultado = 15.5`                     |

Propiedades del Código de Tres Direcciones

1. Una operación por instrucción → Facilita el análisis
2. Variables temporales explícitas → t1, t2, t3, ...
3. Preserva orden de evaluación → Respeta precedencia
4. Optimizable → Fácil aplicar técnicas de optimización
5. Traducible a ensamblador → Mapeo directo a instrucciones de máquina

# **Ejecución del Proyecto**
Uso
Modo Interactivo
```
python analizador_completo.py gramatica.txt
```
Ingresa tu código (termina con línea vacía):
```py
int x;
x = 5 + 3 * 2;
```
## **Ejemplo de Salida Completa**

<img width="674" height="491" alt="image" src="https://github.com/user-attachments/assets/28b382bb-e05e-49d1-b042-a1ef283bbcc6" />

---

<img width="660" height="516" alt="image" src="https://github.com/user-attachments/assets/2f685105-ad7e-404b-86ed-c5cea9585717" />

---
