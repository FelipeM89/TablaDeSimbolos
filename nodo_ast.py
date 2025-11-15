# nodo_ast.py
"""
Estructura de nodos del AST decorado con atributos
"""

class NodoAST:
    """Nodo del árbol de sintaxis abstracta decorado"""
    
    def __init__(self, etiqueta, hijos=None, **atributos):
        self.etiqueta = etiqueta      # Operador, identificador o valor
        self.hijos = hijos or []      # Lista de nodos hijos
        
        # Atributos semánticos
        self.tipo = atributos.get('tipo', None)          # Tipo de dato (int, float, void)
        self.val = atributos.get('val', None)            # Valor calculado
        self.codigo = atributos.get('codigo', "")        # Código intermedio
        self.linea = atributos.get('linea', 0)           # Número de línea
        self.lugar = atributos.get('lugar', None)        # Lugar temporal para código
        
        # Atributos adicionales personalizados
        self.atributos = {k: v for k, v in atributos.items() 
                         if k not in ['tipo', 'val', 'codigo', 'linea', 'lugar']}
    
    def agregar_hijo(self, hijo):
        """Agrega un hijo al nodo"""
        if hijo:
            self.hijos.append(hijo)
    
    def obtener_atributo(self, nombre):
        """Obtiene un atributo personalizado"""
        return self.atributos.get(nombre)
    
    def establecer_atributo(self, nombre, valor):
        """Establece un atributo personalizado"""
        self.atributos[nombre] = valor
    
    def es_hoja(self):
        """Verifica si el nodo es una hoja"""
        return len(self.hijos) == 0
    
    def __str__(self):
        """Representación en string del nodo"""
        partes = [str(self.etiqueta)]
        
        # Agregar atributos relevantes
        atributos_str = []
        if self.tipo:
            atributos_str.append(f"tipo: {self.tipo}")
        if self.val is not None:
            atributos_str.append(f"val: {self.val}")
        
        if atributos_str:
            partes.append(f"[{', '.join(atributos_str)}]")
        
        return " ".join(partes)
    
    def imprimir_decorado(self, nivel=0, es_ultimo=True, prefijo=""):
        """Imprime el AST decorado con todos sus atributos"""
        # Prefijo visual para ramas
        rama = "└── " if es_ultimo else "├── "
        print(prefijo + rama + str(self))
        
        # Calcular nuevo prefijo para los hijos
        if es_ultimo:
            nuevo_prefijo = prefijo + "    "
        else:
            nuevo_prefijo = prefijo + "│   "
        
        # Recorrer hijos
        for i, hijo in enumerate(self.hijos):
            es_ultimo_hijo = (i == len(self.hijos) - 1)
            hijo.imprimir_decorado(nivel + 1, es_ultimo_hijo, nuevo_prefijo)
    
    def obtener_codigo_completo(self):
        """Obtiene todo el código intermedio del subárbol"""
        codigo_completo = []
        
        # Recolectar código de los hijos
        for hijo in self.hijos:
            codigo_hijo = hijo.obtener_codigo_completo()
            if codigo_hijo:
                codigo_completo.append(codigo_hijo)
        
        # Agregar código del nodo actual
        if self.codigo:
            codigo_completo.append(self.codigo)
        
        return "\n".join(codigo_completo)
    
    def calcular_profundidad(self):
        """Calcula la profundidad máxima del árbol"""
        if not self.hijos:
            return 1
        return 1 + max(hijo.calcular_profundidad() for hijo in self.hijos)
    
    def contar_nodos(self):
        """Cuenta el total de nodos en el subárbol"""
        return 1 + sum(hijo.contar_nodos() for hijo in self.hijos)
    
    def buscar_nodos_tipo(self, etiqueta_buscada):
        """Busca todos los nodos con una etiqueta específica"""
        nodos_encontrados = []
        
        if self.etiqueta == etiqueta_buscada:
            nodos_encontrados.append(self)
        
        for hijo in self.hijos:
            nodos_encontrados.extend(hijo.buscar_nodos_tipo(etiqueta_buscada))
        
        return nodos_encontrados


def crear_nodo_operacion(operador, izq, der, linea=0):
    """Crea un nodo para una operación binaria con cálculo de tipo y valor"""
    # Coerción de tipos
    tipo_resultado = coercion_tipos(izq.tipo, der.tipo)
    
    # Cálculo del valor si ambos operandos son constantes
    valor_resultado = None
    if izq.val is not None and der.val is not None:
        try:
            if operador == '+':
                valor_resultado = izq.val + der.val
            elif operador == '-':
                valor_resultado = izq.val - der.val
            elif operador == '*':
                valor_resultado = izq.val * der.val
            elif operador == '/':
                if der.val == 0:
                    raise ValueError(f"Línea {linea}: División por cero")
                valor_resultado = izq.val / der.val
        except Exception as e:
            print(f"⚠️  Advertencia al calcular valor: {e}")
    
    return NodoAST(
        operador,
        hijos=[izq, der],
        tipo=tipo_resultado,
        val=valor_resultado,
        linea=linea
    )


def crear_nodo_numero(lexema, linea=0):
    """Crea un nodo para un número literal"""
    # Determinar tipo basado en el formato
    if '.' in lexema or 'e' in lexema.lower():
        tipo = 'float'
        valor = float(lexema)
    else:
        tipo = 'int'
        valor = int(lexema)
    
    return NodoAST(
        lexema,
        tipo=tipo,
        val=valor,
        linea=linea
    )


def crear_nodo_identificador(nombre, tipo_var, valor=None, linea=0):
    """Crea un nodo para un identificador"""
    return NodoAST(
        nombre,
        tipo=tipo_var,
        val=valor,
        linea=linea
    )


def coercion_tipos(tipo1, tipo2):
    """Realiza coerción de tipos entre dos operandos"""
    if tipo1 is None or tipo2 is None:
        return None
    
    # Si alguno es float, el resultado es float
    if tipo1 == 'float' or tipo2 == 'float':
        return 'float'
    
    # Si ambos son int, el resultado es int
    if tipo1 == 'int' and tipo2 == 'int':
        return 'int'
    
    # Por defecto, devolver el primer tipo
    return tipo1


def tipo_compatible(tipo1, tipo2):
    """Verifica si dos tipos son compatibles para operaciones"""
    tipos_numericos = {'int', 'float'}
    return tipo1 in tipos_numericos and tipo2 in tipos_numericos
