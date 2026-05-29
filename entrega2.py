from simpleai.search import CspProblem, backtrack
import itertools

'''
Contexto
Tras el exitoso regreso del rover Ares-1 con una valiosa colección de muestras marcianas, la misión entra en su siguiente fase crítica: el establecimiento de un campamento base permanente en la superficie del planeta rojo.

El equipo de ingeniería de la misión debe distribuir los módulos del campamento sobre una cuadrícula que representa el terreno explorado. Dado que las reglas de seguridad y operación son numerosas, no es posible hacerlo manualmente de forma confiable. El sistema debe ser capaz de generar automáticamente distribuciones válidas que satisfagan todas las restricciones. Para esto, el problema se modela como un Problema de Satisfacción de Restricciones (CSP).

Descripción del problema
El campamento base se diseña sobre una cuadrícula rectangular de filas × columnas. Cada celda puede contener un único módulo o estar vacía (corredor). Algunas celdas están marcadas de antemano como cráteres y no pueden ser utilizadas bajo ninguna circunstancia.

El sistema debe ubicar los siguientes tipos de módulos:

Tipo	Identificador	Descripción
Módulo habitacional	"hab"	Dormitorios y área de descanso de la tripulación
Generador	"gen"	Planta de energía solar del campamento
Laboratorio	"lab"	Estación científica para el análisis de muestras
Depósito	"dep"	Almacén de suministros y muestras recolectadas
Esclusa de aire	"air"	Punto de entrada y salida hacia la superficie marciana
Restricciones
Sin superposición: no puede haber dos módulos en la misma celda.
Cráteres intransitables: ningún módulo puede ubicarse en una celda marcada como cráter.
Esclusas en el borde: toda esclusa debe estar en el borde del mapa (primera o última fila, o primera o última columna), ya que necesita acceso directo al exterior.
Habitacionales al interior: ningún módulo habitacional puede estar en el borde del mapa; necesitan una capa de protección contra los elementos marcianos.
Seguridad energética: un generador no puede ser adyacente a un módulo habitacional (riesgo de radiación para la tripulación).
Aislamiento entre generadores: dos generadores no pueden ser adyacentes entre sí (interferencia en la red de distribución energética).
Cadena de suministro científico: cada laboratorio debe ser adyacente a al menos un depósito (acceso inmediato a muestras y suministros).
Ruta de evacuación: cada módulo habitacional debe tener al menos una celda adyacente libre (sin módulo ni cráter), que sirva como ruta de emergencia.
Se considera adyacencia ortogonal: arriba, abajo, izquierda y derecha (no diagonal).

Consignas
Ejercicio 1
Formular el problema de diseño del campamento como un CSP usando la biblioteca SimpleAI. Definir con precisión:

Variables: ¿qué elementos del problema hay que determinar?
Dominios: ¿qué valores posibles puede tomar cada variable?
Restricciones: implementar cada una de las ocho restricciones listadas como funciones compatibles con SimpleAI, indicando sobre qué variables actúa cada una.
Ejercicio 2
Implementar la función build_camp con la siguiente interfaz exacta:

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    ...
Parámetros:

camp_size: tupla (filas, columnas) con las dimensiones de la cuadrícula.
habs: entero, cantidad de módulos habitacionales a ubicar.
generators: entero, cantidad de generadores a ubicar.
labs: entero, cantidad de laboratorios a ubicar.
deposits: entero, cantidad de depósitos a ubicar.
airlocks: entero, cantidad de esclusas a ubicar.
craters: lista de tuplas (fila, columna) con las celdas inaccesibles.
Resultado:

Lista de tuplas (tipo, fila, columna), donde tipo es uno de "hab", "gen", "lab", "dep" o "air". Las filas y columnas son índices base 0.

Si no existe ninguna distribución válida que satisfaga todas las restricciones, retornar None.

Ejemplo de uso:

resultado = build_camp(
    camp_size=(5, 6),
    habs=2,
    generators=1,
    labs=1,
    deposits=2,
    airlocks=1,
    craters=[(2, 2), (2, 3)],
)
# Una posible salida válida:
# [
#     ("air", 0, 3),
#     ("hab", 2, 1), ("hab", 2, 4),
#     ("gen", 4, 4),
#     ("lab", 3, 2),
#     ("dep", 3, 1), ("dep", 3, 3),
# ]
Importante: el módulo no debe ejecutar el CSP al momento de ser importado. Toda lógica de resolución debe estar dentro de la función build_camp.
'''
def son_adyacentes(pos1, pos2):
    f1, c1 = pos1
    f2, c2 = pos2
    return (f1 == f2 and abs(c1 - c2) == 1) or (c1 == c2 and abs(f1 - f2) == 1)

def no_sean_adyacentes(variables, valores):
    # valores[0] es la posición del módulo 1, valores[1] la del módulo 2
    return not son_adyacentes(valores[0], valores[1])

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    
    #variables
    variables = []
    for g in range(generators): variables.append(f'gen{g}')
    for h in range(habs): variables.append(f'hab{h}')
    for l in range(labs): variables.append(f'lab{l}')
    for d in range(deposits): variables.append(f'dep{d}')
    for a in range(airlocks): variables.append(f'air{a}')
    
    #dominios
    filas, columnas = camp_size    

    posiciones_validas = []

    for f in range(filas):
        for c in range(columnas):
            if (f, c) not in craters: 
                posiciones_validas.append((f, c))

    posiciones_validas_bordes = []

    for f in range(filas):
        for c in range(columnas):
            if (f, c) not in craters and (f == 0 or f == filas - 1 or c == 0 or c == columnas - 1):
                posiciones_validas_bordes.append((f, c))

    posiciones_validas_interior = []

    for p in posiciones_validas:
        if p not in posiciones_validas_bordes:
            f, c = p
            posiciones_validas_interior.append((f, c))

    dominio = {}

    for var in variables:
        if var.startswith('air'):
            dominio[var] = posiciones_validas_bordes
        elif var.startswith('hab'):
            dominio[var] = posiciones_validas_interior
        else:
            dominio[var] = posiciones_validas

    #restricciones
    restricciones = []

    #R1: Sin superposición
    def sin_superposicion(variables, values):
        return values[0] != values[1]
    
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            restricciones.append(((variables[i], variables[j]), sin_superposicion))

    #R2: Cráteres intransitables (ya se manejan al definir el dominio)

    #R3: Esclusas en el borde (ya se manejan al definir el dominio)

    #R4: Habitacionales al interior (ya se manejan al definir el dominio)

    #R5: Seguridad energética
    def seguridad_energetica(variables, values):
        return not son_adyacentes(values[0], values[1])

    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            if (variables[i].startswith('gen') and variables[j].startswith('hab')) or (variables[i].startswith('hab') and variables[j].startswith('gen')):
                    restricciones.append(((variables[i], variables[j]), seguridad_energetica))
 
    
    #R6: Aislamiento entre generadores
    def aislamiento_generadores(variables, values):
        return not son_adyacentes(values[0], values[1])

    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            if variables[i].startswith('gen') and variables[j].startswith('gen'):
                restricciones.append(((variables[i], variables[j]), aislamiento_generadores))
    
    #R7: Cadena de suministro científico
    def cadena_suministro_arb(variables, valores):
        pos_laboratorio = valores[0]
        pos_depositos = valores[1:]
        
        for pos_dep in pos_depositos:
            if son_adyacentes(pos_laboratorio, pos_dep):
                return True 
                
        return False 
        
    lista_depositos = [v for v in variables if v.startswith('dep')]

    for var in variables:
        if var.startswith('lab'):
            grupo_variables = [var] + lista_depositos
            restricciones.append((tuple(grupo_variables), cadena_suministro_arb))
    
    #R8: Ruta de evacuación
    def ruta_evacuacion_arb(variables, valores):
        pos_hab = valores[0]
        pos_ocupadas_otros = valores[1:]
        f, c = pos_hab
        
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for df, dc in direcciones:
            nf, nc = f + df, c + dc
            
            if 0 <= nf < filas and 0 <= nc < columnas:
                pos_vecina = (nf, nc)
                
                if pos_vecina not in craters and pos_vecina not in pos_ocupadas_otros:
                    return True 
                    
        return False 
    
    for var in variables:
        if var.startswith('hab'):
            resto_variables = [v for v in variables if v != var]
            
            grupo_evacuacion = [var] + resto_variables
            restricciones.append((tuple(grupo_evacuacion), ruta_evacuacion_arb))

    #resolver el CSP
    problema = CspProblem(variables, dominio, restricciones)
    solucion = backtrack(problema)
    
    if solucion is None:
        return None

    resultado_final = []

    for var, pos in solucion.items():

        if var.startswith('gen'):
            tipo = 'gen'
        elif var.startswith('hab'):
            tipo = 'hab'
        elif var.startswith('lab'):
            tipo = 'lab'
        elif var.startswith('dep'):
            tipo = 'dep'
        elif var.startswith('air'):
            tipo = 'air'

        f, c = pos
        resultado_final.append((tipo, f, c))

    return resultado_final