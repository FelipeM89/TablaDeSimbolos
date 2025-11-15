# tabla_simbolos.py
"""
Gestión de la tabla de símbolos con soporte para alcances anidados
"""

class Simbolo:
    """Representa un símbolo en la tabla"""
    def __init__(self, nombre, tipo, alcance, linea, valor=None):
        self.nombre = nombre
        self.tipo = tipo          # 'int', 'float', etc.
        self.alcance = alcance    # nivel de anidamiento
        self.linea = linea        # línea de declaración
        self.valor = valor        # valor asignado (opcional)
        self.usado = False        # si ha sido referenciado
    
    def __str__(self):
        return f"{self.nombre:10} {self.tipo:8} {self.alcance:8} {self.linea:6} {str(self.valor):10} {'Sí' if self.usado else 'No':5}"

class TablaSimbolos:
    """Tabla de símbolos con manejo de alcances"""
    def __init__(self):
        self.tabla = {}           # {nombre: [Simbolo]} - lista para múltiples alcances
        self.alcance_actual = 0   # nivel de alcance actual
        self.pila_alcances = [{}] # pila de diccionarios {nombre: Simbolo}
        self.errores = []
        self.warnings = []
    
    def entrar_alcance(self):
        """Crea un nuevo nivel de alcance"""
        self.alcance_actual += 1
        self.pila_alcances.append({})
    
    def salir_alcance(self):
        """Sale del alcance actual y verifica variables no usadas"""
        if self.alcance_actual > 0:
            alcance_saliente = self.pila_alcances.pop()
            # Verificar variables no usadas
            for nombre, simbolo in alcance_saliente.items():
                if not simbolo.usado:
                    self.warnings.append(
                        f"Línea {simbolo.linea}: Variable '{nombre}' declarada pero no usada"
                    )
            self.alcance_actual -= 1
    
    def insertar(self, nombre, tipo, linea, valor=None):
        """Inserta un símbolo en el alcance actual"""
        # Verificar redeclaración en el mismo alcance
        if nombre in self.pila_alcances[self.alcance_actual]:
            simbolo_anterior = self.pila_alcances[self.alcance_actual][nombre]
            self.errores.append(
                f"Línea {linea}: Error semántico - Variable '{nombre}' ya declarada en línea {simbolo_anterior.linea}"
            )
            return False
        
        # Crear e insertar el símbolo
        simbolo = Simbolo(nombre, tipo, self.alcance_actual, linea, valor)
        self.pila_alcances[self.alcance_actual][nombre] = simbolo
        
        # Agregar a la lista global de símbolos
        if nombre not in self.tabla:
            self.tabla[nombre] = []
        self.tabla[nombre].append(simbolo)
        
        return True
    
    def buscar(self, nombre):
        """Busca un símbolo desde el alcance actual hacia arriba"""
        # Buscar desde el alcance actual hacia el global
        for i in range(self.alcance_actual, -1, -1):
            if nombre in self.pila_alcances[i]:
                return self.pila_alcances[i][nombre]
        return None
    
    def existe(self, nombre):
        """Verifica si un símbolo existe en algún alcance visible"""
        return self.buscar(nombre) is not None
    
    def existe_en_alcance_actual(self, nombre):
        """Verifica si existe en el alcance actual (para detectar redeclaraciones)"""
        return nombre in self.pila_alcances[self.alcance_actual]
    
    def obtener_tipo(self, nombre):
        """Obtiene el tipo de una variable"""
        simbolo = self.buscar(nombre)
        return simbolo.tipo if simbolo else None
    
    def obtener_valor(self, nombre):
        """Obtiene el valor de una variable"""
        simbolo = self.buscar(nombre)
        return simbolo.valor if simbolo else None
    
    def actualizar_valor(self, nombre, valor):
        """Actualiza el valor de una variable"""
        simbolo = self.buscar(nombre)
        if simbolo:
            simbolo.valor = valor
            return True
        return False
    
    def marcar_usado(self, nombre):
        """Marca una variable como usada"""
        simbolo = self.buscar(nombre)
        if simbolo:
            simbolo.usado = True
    
    def validar_declaracion(self, nombre, linea):
        """Valida que una variable esté declarada antes de usarse"""
        if not self.existe(nombre):
            self.errores.append(
                f"Línea {linea}: Error semántico - Variable '{nombre}' no declarada"
            )
            return False
        self.marcar_usado(nombre)
        return True
    
    def imprimir(self):
        """Imprime la tabla de símbolos"""
        print("\n" + "="*80)
        print(" TABLA DE SÍMBOLOS ".center(80, "="))
        print("="*80)
        print(f"{'Nombre':10} {'Tipo':8} {'Alcance':8} {'Línea':6} {'Valor':10} {'Usado':5}")
        print("-"*80)
        
        # Recolectar todos los símbolos únicos por alcance
        simbolos_mostrados = set()
        for i in range(len(self.pila_alcances)):
            for nombre, simbolo in self.pila_alcances[i].items():
                id_simbolo = (nombre, simbolo.alcance)
                if id_simbolo not in simbolos_mostrados:
                    print(simbolo)
                    simbolos_mostrados.add(id_simbolo)
        
        print("="*80)
    
    def imprimir_errores(self):
        """Imprime los errores semánticos encontrados"""
        if self.errores:
            print("\n" + "="*80)
            print(" ERRORES SEMÁNTICOS ".center(80, "="))
            print("="*80)
            for error in self.errores:
                print(f"❌ {error}")
            print("="*80)
    
    def imprimir_warnings(self):
        """Imprime las advertencias"""
        if self.warnings:
            print("\n" + "="*80)
            print(" ADVERTENCIAS ".center(80, "="))
            print("="*80)
            for warning in self.warnings:
                print(f"⚠️  {warning}")
            print("="*80)
    
    def tiene_errores(self):
        """Retorna True si hay errores semánticos"""
        return len(self.errores) > 0