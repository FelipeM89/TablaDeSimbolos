#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# analizador_completo.py
"""
Analizador completo con ETDS para expresiones aritméticas
Incluye análisis léxico, sintáctico y semántico
"""

import re
import sys
from tabla_simbolos import TablaSimbolos
from nodo_ast import (NodoAST, crear_nodo_operacion, crear_nodo_numero, 
                      crear_nodo_identificador)

class AnalizadorLexico:
    """Analizador léxico para tokenizar la entrada"""
    
    def __init__(self, cadena):
        self.cadena = cadena
        self.pos = 0
        self.linea_actual = 1
        
        # Definición de tokens
        self.tokens_pattern = [
            ('TIPO', r'\b(int|float)\b'),
            ('NUM', r'\d+\.\d+|\d+'),
            ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),
            ('MAS', r'\+'),
            ('MENOS', r'-'),
            ('MUL', r'\*'),
            ('DIV', r'/'),
            ('PARI', r'\('),
            ('PARD', r'\)'),
            ('PUNTOCOMA', r';'),
            ('IGUAL', r'='),
            ('ESPACIOS', r'[ \t]+'),
            ('NEWLINE', r'\n'),
        ]
        
        # Compilar expresiones regulares
        self.regex_tokens = [(nombre, re.compile(patron)) 
                            for nombre, patron in self.tokens_pattern]
    
    def siguiente_token(self):
        """Obtiene el siguiente token de la entrada"""
        if self.pos >= len(self.cadena):
            return None
        
        # Intentar emparejar cada patrón
        for nombre, regex in self.regex_tokens:
            match = regex.match(self.cadena, self.pos)
            if match:
                lexema = match.group(0)
                self.pos = match.end()
                
                # Ignorar espacios
                if nombre == 'ESPACIOS':
                    return self.siguiente_token()
                
                # Incrementar contador de líneas
                if nombre == 'NEWLINE':
                    self.linea_actual += 1
                    return self.siguiente_token()
                
                return {
                    'tipo': nombre,
                    'lexema': lexema,
                    'linea': self.linea_actual
                }
        
        # Carácter no reconocido
        raise ValueError(f"Línea {self.linea_actual}: Carácter no reconocido '{self.cadena[self.pos]}'")
    
    def tokenizar(self):
        """Tokeniza toda la entrada"""
        tokens = []
        while self.pos < len(self.cadena):
            token = self.siguiente_token()
            if token:
                tokens.append(token)
        return tokens


class GeneradorCodigo:
    """Generador de código intermedio de tres direcciones"""
    
    def __init__(self):
        self.contador_temporal = 0
        self.codigo_generado = []
    
    def nuevo_temporal(self):
        """Genera un nuevo nombre de variable temporal"""
        self.contador_temporal += 1
        return f"t{self.contador_temporal}"
    
    def generar(self, instruccion):
        """Agrega una instrucción al código generado"""
        self.codigo_generado.append(instruccion)
    
    def obtener_codigo(self):
        """Retorna todo el código generado"""
        return "\n".join(self.codigo_generado)
    
    def reset(self):
        """Reinicia el generador"""
        self.contador_temporal = 0
        self.codigo_generado = []


class AnalizadorSintactico:
    """Analizador sintáctico con ETDS"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.tabla_simbolos = TablaSimbolos()
        self.generador = GeneradorCodigo()
    
    def actual(self):
        """Retorna el token actual sin consumirlo"""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def consumir(self, tipo_esperado=None):
        """Consume el token actual si coincide con el tipo esperado"""
        token = self.actual()
        if token is None:
            return None
        
        if tipo_esperado is None or token['tipo'] == tipo_esperado:
            self.pos += 1
            return token
        
        raise SyntaxError(f"Línea {token['linea']}: Se esperaba {tipo_esperado}, se encontró {token['tipo']}")
    
    def parsear(self):
        """Punto de entrada del analizador - S"""
        nodos = []
        
        while self.actual():
            token = self.actual()
            
            # Declaración: tipo id ;
            if token['tipo'] == 'TIPO':
                nodo = self.parsear_declaracion()
                if nodo:
                    nodos.append(nodo)
            
            # Asignación o expresión: id = E ; o E
            elif token['tipo'] in ['ID', 'NUM', 'PARI']:
                nodo = self.parsear_asignacion_o_expresion()
                if nodo:
                    nodos.append(nodo)
            
            else:
                raise SyntaxError(f"Línea {token['linea']}: Token inesperado {token['tipo']}")
        
        # Crear nodo raíz del programa
        return NodoAST("Programa", hijos=nodos, tipo='void')
    
    def parsear_declaracion(self):
        """D → tipo id ;"""
        token_tipo = self.consumir('TIPO')
        tipo = token_tipo['lexema']
        linea = token_tipo['linea']
        
        token_id = self.consumir('ID')
        if not token_id:
            raise SyntaxError(f"Línea {linea}: Se esperaba un identificador después del tipo")
        
        nombre = token_id['lexema']
        
        self.consumir('PUNTOCOMA')
        
        # Acción semántica: insertar en tabla de símbolos
        self.tabla_simbolos.insertar(nombre, tipo, linea)
        
        # Generar código intermedio
        self.generador.generar(f"declare {nombre} : {tipo}")
        
        return NodoAST(
            "Declaracion",
            hijos=[
                NodoAST(tipo, tipo='tipo'),
                NodoAST(nombre, tipo=tipo, linea=linea)
            ],
            tipo='void',
            linea=linea
        )
    
    def parsear_asignacion_o_expresion(self):
        """Detecta si es asignación (id = E ;) o solo expresión (E)"""
        # Guardar posición por si necesitamos retroceder
        pos_guardada = self.pos
        
        # Intentar parsear como asignación
        token = self.actual()
        if token and token['tipo'] == 'ID':
            nombre = token['lexema']
            linea = token['linea']
            self.consumir('ID')
            
            # Si viene '=', es asignación
            if self.actual() and self.actual()['tipo'] == 'IGUAL':
                self.consumir('IGUAL')
                
                # Validar que la variable esté declarada
                if not self.tabla_simbolos.validar_declaracion(nombre, linea):
                    # Continuar parseando pero marcar error
                    pass
                
                # Parsear la expresión
                nodo_expr = self.parsear_E()
                
                self.consumir('PUNTOCOMA')
                
                # Actualizar valor en tabla de símbolos
                if nodo_expr.val is not None:
                    self.tabla_simbolos.actualizar_valor(nombre, nodo_expr.val)
                
                # Generar código intermedio
                if nodo_expr.lugar:
                    self.generador.generar(f"{nombre} = {nodo_expr.lugar}")
                elif nodo_expr.val is not None:
                    self.generador.generar(f"{nombre} = {nodo_expr.val}")
                
                tipo_var = self.tabla_simbolos.obtener_tipo(nombre)
                
                return NodoAST(
                    "Asignacion",
                    hijos=[
                        crear_nodo_identificador(nombre, tipo_var, linea=linea),
                        nodo_expr
                    ],
                    tipo=tipo_var,
                    val=nodo_expr.val,
                    linea=linea
                )
        
        # Si no es asignación, retroceder y parsear como expresión
        self.pos = pos_guardada
        nodo_expr = self.parsear_E()
        
        # Consumir punto y coma opcional
        if self.actual() and self.actual()['tipo'] == 'PUNTOCOMA':
            self.consumir('PUNTOCOMA')
        
        return nodo_expr
    
    def parsear_E(self):
        """E → E + T | E - T | T"""
        nodo = self.parsear_T()
        
        while self.actual() and self.actual()['tipo'] in ['MAS', 'MENOS']:
            token_op = self.consumir()
            operador = token_op['lexema']
            linea = token_op['linea']
            
            nodo_derecho = self.parsear_T()
            
            # Crear nodo de operación con atributos calculados
            nodo_nuevo = crear_nodo_operacion(operador, nodo, nodo_derecho, linea)
            
            # Generar código intermedio
            temp = self.generador.nuevo_temporal()
            izq_lugar = nodo.lugar if nodo.lugar else nodo.val if nodo.val is not None else nodo.etiqueta
            der_lugar = nodo_derecho.lugar if nodo_derecho.lugar else nodo_derecho.val if nodo_derecho.val is not None else nodo_derecho.etiqueta
            
            self.generador.generar(f"{temp} = {izq_lugar} {operador} {der_lugar}")
            nodo_nuevo.lugar = temp
            
            nodo = nodo_nuevo
        
        return nodo
    
    def parsear_T(self):
        """T → T * F | T / F | F"""
        nodo = self.parsear_F()
        
        while self.actual() and self.actual()['tipo'] in ['MUL', 'DIV']:
            token_op = self.consumir()
            operador = token_op['lexema']
            linea = token_op['linea']
            
            nodo_derecho = self.parsear_F()
            
            # Verificar división por cero
            if operador == '/' and nodo_derecho.val == 0:
                self.tabla_simbolos.errores.append(
                    f"Línea {linea}: Error semántico - División por cero"
                )
            
            # Crear nodo de operación
            nodo_nuevo = crear_nodo_operacion(operador, nodo, nodo_derecho, linea)
            
            # Generar código intermedio
            temp = self.generador.nuevo_temporal()
            izq_lugar = nodo.lugar if nodo.lugar else nodo.val if nodo.val is not None else nodo.etiqueta
            der_lugar = nodo_derecho.lugar if nodo_derecho.lugar else nodo_derecho.val if nodo_derecho.val is not None else nodo_derecho.etiqueta
            
            self.generador.generar(f"{temp} = {izq_lugar} {operador} {der_lugar}")
            nodo_nuevo.lugar = temp
            
            nodo = nodo_nuevo
        
        return nodo
    
    def parsear_F(self):
        """F → ( E ) | num | id"""
        token = self.actual()
        
        if not token:
            raise SyntaxError("Fin inesperado de entrada")
        
        linea = token['linea']
        
        # ( E )
        if token['tipo'] == 'PARI':
            self.consumir('PARI')
            nodo = self.parsear_E()
            self.consumir('PARD')
            return nodo
        
        # num
        if token['tipo'] == 'NUM':
            self.consumir('NUM')
            return crear_nodo_numero(token['lexema'], linea)
        
        # id
        if token['tipo'] == 'ID':
            nombre = token['lexema']
            self.consumir('ID')
            
            # Validar que esté declarada
            if not self.tabla_simbolos.validar_declaracion(nombre, linea):
                # Retornar nodo con tipo desconocido
                return NodoAST(nombre, tipo=None, linea=linea)
            
            tipo_var = self.tabla_simbolos.obtener_tipo(nombre)
            valor = self.tabla_simbolos.obtener_valor(nombre)
            
            return crear_nodo_identificador(nombre, tipo_var, valor, linea)
        
        raise SyntaxError(f"Línea {linea}: Token inesperado {token['tipo']}")


def main():
    """Función principal"""
    print("="*80)
    print(" ANALIZADOR CON ETDS - EXPRESIONES ARITMÉTICAS ".center(80, "="))
    print("="*80)
    
    # Leer entrada
    if len(sys.argv) > 2:
        # Leer desde archivo
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            entrada = f.read()
        print(f"\n📄 Archivo: {sys.argv[2]}")
    else:
        # Leer desde consola
        print("\nIngrese el código (termine con una línea vacía):")
        lineas = []
        while True:
            try:
                linea = input()
                if not linea:
                    break
                lineas.append(linea)
            except EOFError:
                break
        entrada = "\n".join(lineas)
    
    print(f"\n📝 Entrada:")
    print("-"*80)
    print(entrada)
    print("-"*80)
    
    try:
        # Análisis léxico
        lexico = AnalizadorLexico(entrada)
        tokens = lexico.tokenizar()
        
        print(f"\n🔤 Tokens generados: {len(tokens)}")
        
        # Análisis sintáctico y semántico
        sintactico = AnalizadorSintactico(tokens)
        ast = sintactico.parsear()
        
        # Verificar errores semánticos
        if sintactico.tabla_simbolos.tiene_errores():
            print("\n❌ ANÁLISIS FALLIDO - Errores semánticos encontrados")
            sintactico.tabla_simbolos.imprimir_errores()
        else:
            print("\n✅ ANÁLISIS EXITOSO")
            
            # Mostrar tabla de símbolos
            sintactico.tabla_simbolos.imprimir()
            
            # Mostrar AST decorado
            print("\n" + "="*80)
            print(" AST DECORADO ".center(80, "="))
            print("="*80)
            ast.imprimir_decorado()
            print("="*80)
            
            # Mostrar código intermedio
            print("\n" + "="*80)
            print(" CÓDIGO INTERMEDIO (3 DIRECCIONES) ".center(80, "="))
            print("="*80)
            codigo = sintactico.generador.obtener_codigo()
            if codigo:
                print(codigo)
            else:
                print("(sin código generado)")
            print("="*80)
            
            # Mostrar estadísticas del AST
            print(f"\n📊 Estadísticas del AST:")
            print(f"   - Nodos totales: {ast.contar_nodos()}")
            print(f"   - Profundidad máxima: {ast.calcular_profundidad()}")
        
        # Mostrar advertencias
        sintactico.tabla_simbolos.salir_alcance()  # Para detectar variables no usadas
        sintactico.tabla_simbolos.imprimir_warnings()
        
    except (ValueError, SyntaxError) as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    
    print("\n" + "="*80)
    return 0


if __name__ == "__main__":
    sys.exit(main())