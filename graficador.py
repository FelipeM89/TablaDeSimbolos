# graficador.py
class Graficador:
    @staticmethod
    def imprimir_arbol(nodo, nivel=0, es_ultimo=True, prefijo=""):
        """
        Imprime un árbol en consola usando líneas y sangrías.

        nodo: instancia de NodoAST
        nivel: profundidad del nodo
        es_ultimo: indica si el nodo es el último hijo
        prefijo: prefijo acumulado para dibujar ramas
        """

        # Prefijo visual para ramas
        rama = "└── " if es_ultimo else "├── "
        print(prefijo + rama + str(nodo.etiqueta))

        # Calcular nuevo prefijo para los hijos
        if es_ultimo:
            nuevo_prefijo = prefijo + "    "
        else:
            nuevo_prefijo = prefijo + "│   "

        # Recorrer hijos
        for i, hijo in enumerate(nodo.hijos):
            es_ultimo_hijo = (i == len(nodo.hijos) - 1)
            Graficador.imprimir_arbol(hijo, nivel + 1, es_ultimo_hijo, nuevo_prefijo)