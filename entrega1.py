from simpleai.search import astar, SearchProblem
from simpleai.search.viewers import ConsoleViewer

class ProblemaRover(SearchProblem):
    '''
    Tenemos que almacenar en el estado la siguiente información: batería, posición del rover, carga, herramienta, muestras por recoger 
    (igneas y sedimentarias).

    Se desea programar el sistema de navegación para el explorador Ares-1 en Marte. El rover aterriza en una grilla que representa la superficie marciana. Su objetivo es juntar todas las muestras de rocas en el menor tiempo posible y dejar pequeñas "cápsulas" de muestras en el suelo, que luego serán recogidas por una futura misión.

    Pero existen algunas restricciones:

    Requisitos de herramientas: Existen dos tipos de muestras de rocas. Las rocas Ígneas requieren un taladro térmico, mientras que las rocas Sedimentarias requieren un taladro de percusión (nunca hay dos tipos de piedra diferentes en el mismo lugar). Y el rover solo puede tener activo un taladro a la vez, cambiar de taladro es una acción que cuesta tiempo y consume batería.
    Capacidad de carga: El rover puede llevar un máximo de 2 muestras al mismo tiempo. Para recolectar más, primero debe vaciar su carga actual depositando las cápsulas de muestras en el suelo (en cualquier parte del mapa).
    Batería limitada: El rover tiene batería limitada, si en algún momento se queda sin batería se perdería para siempre. Por ello, su batería nunca debe llegar a 0.
    Para cumplir con su objetivo, el rover puede ejecutar las siguientes acciones:

    Moverse: A cualquier celda adyacente (arriba, abajo, izquierda, derecha). Toma 1 minuto, consume 1 unidad de batería.

    Sobremarcha (Overdrive): Moverse exactamente 2 celdas en línea recta (saltando por encima de la celda intermedia). Toma 1 minuto, consume 4 unidades de batería.

    Equipar taladro: Cambia el taladro activo por el otro tipo (o equipa uno si todavía no tiene un taladro activo). Toma 3 minutos, consume 1 unidad de batería.

    Perforar y recolectar: Si está en una celda con una muestra, tiene el taladro correcto equipado y tiene espacio disponible en la bodega de carga. Toma 2 minutos, consume 3 unidades de batería.

    Depositar cápsula con muestras: Si tiene carga, vacía todas las muestras de la bodega de carga y las deja en una cápsula en el piso. Toma 1 minuto por muestra entregada, consume 1 unidad de batería. Para armar una cápsula es necesario que el rover tenga 2 muestras cargadas, a menos que sea la última existente.

    Desplegar paneles solares: El rover se detiene para recargar. Toma 4 minutos, restaura 10 unidades de batería (hasta el límite máximo de 20). Restricción: No se puede realizar esta acción en las "zonas de sombra" (coordenadas específicas provistas en el mapa).

    Implementación
    La implementación consistirá en tener una función planear_rover que recibirá como parámetros:

    # todas las coordenadas son en formato (fila, columna)
    acciones = planear_rover(
        rover_inicio=(0, 0),
        bateria_inicial=20,
        zonas_sombra=[(0, 1), (0, 2)],
        muestras_igneas=[(1, 1), (1, 2)],
        muestras_sedimentarias=[(2, 3)],
    )
    Los valores de los parámetros pueden cambiar, y vamos a probar con diferentes escenarios posibles de distintos niveles de complejidad.

    El resultado deberá ser una lista de las acciones a realizar. Cada acción debe ser una tupla con el siguiente formato: (str_tipo_accion, parametro_opcional).

    Los tipos de acciones son los siguientes:

    "moverse": para estas acciones, el segundo elemento de la tupla debe ser las coordenadas hacia donde se mueve el rover. Por ejemplo: ("moverse", (2, 4)).
    "sobremarcha": para estas acciones, el segundo elemento de la tupla debe ser las coordenadas hacia donde se mueve el rover. Por ejemplo: ("sobremarcha", (2, 5)).
    "equipar": equipar un tipo de taladro. El segundo elemento de la tupla es el tipo de taladro a equipar, que puede ser "termico" o "percusión". Ejemplo: ("equipar", "termico").
    "recolectar": recolectar una muestra. El segundo elemento de la tupla es el tipo de muestra a recolectar, que puede ser "ignea" o "sedimentaria". Ejemplo: ("recolectar", "ignea").
    "depositar": deposita la carga en piso, vaciando la bahía de carga. No requiere un segundo elemento, por lo que se debe dejar como None. Ejemplo: ("entregar", None).
    "recargar": desplegar paneles solares para recargar la batería. No requiere un segundo elemento, por lo que se debe dejar como None. Ejemplo: ("recargar", None).
    Por ejemplo, un resultado (incompleto, ilustrativo) podría ser el siguiente:

    print(acciones)
    [
        ("moverse", (0, 1)),
        ("moverse", (0, 2)),
        ("recargar", None),
        ("moverse", (1, 2)),
        ("moverse", (2, 2)),
        ("equipar", "termico"),
        ("moverse", (3, 2)),
        ("moverse", (3, 3)),
        ("recolectar", "ignea"),
        ("moverse", (3, 4)),
        ("recolectar", "ignea"),
        ("depositar", None),
        ...  # y así hasta resolver todo el problema
    ]
    La secuencia de acciones tiene que ser válida (se tienen que poder realizar esos movimientos bajo las restricciones explicadas). Y tiene que ser la secuencia de acciones que menos tiempo requiera para conseguir el objetivo.

    Todos los casos que vamos a probar son resolubles.

    Ejercicios:
    Implementar la formulación del problema como problema de búsqueda tradicional para ser resuelto con SimpleAI, incluyendo definición de la clase problema y sus métodos: cost, actions, result, is_goal y heuristic (la heurística puede ser poco precisa, pero debe ser admisible).

    Implementar la función planear_rover con exactamente la api detallada en la sección anterior (tanto para los datos esperados de entrada, como para el resultado devuelto).

    Utilizar algún agente o editor de código asistido por IA (como Claude Code, Codex, Copilot, etc) para resolver el problema: presentarle la consigna y pedirle que la resuelva utilizando SimpleAI. Luego comparar la solución que les dio con la que ustedes implementaron, y analizar las diferencias entre ambas: qué diferencias hay en el enfoque (estado, acciones, heurística, etc)? Logró resolverlo pasando todos los tests? Cómo se comparan en pérformance? Escribir las conclusiones en no más de 4 párrafos.
    '''

    # todas las coordenadas son en formato (fila, columna)
    def __init__(self, rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):

        self.zonas_sombra = tuple(zonas_sombra)

        self.capacidad_maxima = 2
        self.bateria_maxima = 20

        inicial = (
            bateria_inicial,       # batería actual
            rover_inicio,          # posición actual del rover
            tuple(),               # carga actual (puede empezar vacía)
            None,                  # taladro activo (None al inicio)
            tuple(muestras_igneas),
            tuple(muestras_sedimentarias),
        )

        super(ProblemaRover, self).__init__(inicial)

    # is_goal
    def is_goal(self, state):
        return (len(state[4]) == 0) and (len(state[5]) == 0) and (len(state[2]) == 0)
    
    # actions
    def actions(self, state):
        
        acciones = [] 

        bateria, posicion, carga, taladro, igneas, sedimentarias = state

        fila, columna = posicion

        if len(igneas) + len(sedimentarias) == 0 and len(carga) == 0:

            return tuple(acciones)

        # movimientos normales
        movimientos = [("moverse", (fila-1, columna)), 
                       ("moverse", (fila+1, columna)), 
                       ("moverse", (fila, columna-1)), 
                       ("moverse", (fila, columna+1))]
        
        if bateria > 1:
            for m in movimientos:
                acciones.append(m)

        # sobremarcha
        sobremarcha_movimientos = [("sobremarcha", (fila-2, columna)), 
                                   ("sobremarcha", (fila+2, columna)), 
                                   ("sobremarcha", (fila, columna-2)), 
                                   ("sobremarcha", (fila, columna+2))]
        
        if bateria > 4:
            for m in sobremarcha_movimientos:
                acciones.append(m)

        # equipar taladro
        if bateria > 1:
            
            if taladro != "termico" and posicion in igneas:
                acciones.append(("equipar", "termico"))

            if taladro != "percusion" and posicion in sedimentarias:
                acciones.append(("equipar", "percusion"))
        
        # recolectar
        if bateria > 3:
            if (posicion in igneas) and (taladro == "termico") and (len(carga) < self.capacidad_maxima):
                acciones.append(("recolectar", "ignea"))
            
            if (posicion in sedimentarias) and (taladro == "percusion") and (len(carga) < self.capacidad_maxima):
                acciones.append(("recolectar", "sedimentaria"))

        # depositar
        if bateria > 1:
            if len(carga) == 2:
                acciones.append(("depositar", None))
            elif (len(carga) == 1) and (len(igneas) + len(sedimentarias) == 0):
                acciones.append(("depositar", None))

        # recargar
        if posicion not in self.zonas_sombra:
            if bateria < self.bateria_maxima:
                acciones.append(("recargar", None))

        return acciones

    # result
    def result(self, state, action):

        bateria, posicion, carga, taladro, igneas, sedimentarias = state

        tipo_accion, parametro = action

        # moverse
        if tipo_accion == "moverse":
            nueva_posicion = parametro
            return (bateria - 1, nueva_posicion, carga, taladro, igneas, sedimentarias)

        # sobremarcha
        elif tipo_accion == "sobremarcha":
            nueva_posicion = parametro
            return (bateria - 4, nueva_posicion, carga, taladro, igneas, sedimentarias)
        
        # equipar
        elif tipo_accion == "equipar":
            nuevo_taladro = parametro
            return (bateria - 1, posicion, carga, nuevo_taladro, igneas, sedimentarias)
        
        # recolectar
        elif tipo_accion == "recolectar":
            tipo_muestra = parametro
            if tipo_muestra == "ignea":
                nueva_carga = carga + ("ignea",)

                lista_igneas = list(igneas)
                lista_igneas.remove(posicion)
                nuevas_igneas = tuple(lista_igneas)

                return (bateria - 3, posicion, nueva_carga, taladro, nuevas_igneas, sedimentarias)
            elif tipo_muestra == "sedimentaria":
                nueva_carga = carga + ("sedimentaria",)

                lista_sedimentarias = list(sedimentarias)
                lista_sedimentarias.remove(posicion)
                nuevas_sedimentarias = tuple(lista_sedimentarias)

                return (bateria - 3, posicion, nueva_carga, taladro, igneas, nuevas_sedimentarias)

        # depositar
        elif tipo_accion == "depositar":
            return (bateria - 1, posicion, tuple(), taladro, igneas, sedimentarias)
        
        # recargar
        elif tipo_accion == "recargar":
            nueva_bateria = min(bateria + 10, self.bateria_maxima)
            return (nueva_bateria, posicion, carga, taladro, igneas, sedimentarias)
   
    # cost
    def cost(self, state, action, result):

        tipo_accion, parametro = action
        bateria, posicion, carga, taladro, igneas, sedimentarias = state

        # moverse
        if tipo_accion == "moverse":
            return 1
        
        # sobremarcha
        elif tipo_accion == "sobremarcha":
            return 1
        
        # equipar
        elif tipo_accion == "equipar":
            return 3
        
        # recolectar
        elif tipo_accion == "recolectar":
            return 2
        
        # depositar
        elif tipo_accion == "depositar":
            
            if len(carga) == 2:
                return 2
            else:
                return 1
        
        # recargar
        elif tipo_accion == "recargar":
            return 4
    
    # manhattan 
    def manhattan(self, pos1, pos2):

        x1, y1 = pos1
        x2, y2 = pos2

        return abs(x2 - x1) + abs(y2 - y1)

    # heuristic
    def heuristic(self, state):
        
        bateria, posicion, carga, taladro, igneas, sedimentarias = state

        muestras_restantes = len(igneas) + len(sedimentarias)
        distancias = []
        tiempo = 0
        
        if muestras_restantes > 0:

            tiempo_taladro = 0

            if taladro == "termico" and len(sedimentarias) > 0:
                tiempo_taladro = 3
            elif taladro == "percusion" and len(igneas) > 0:
                tiempo_taladro = 3
            elif taladro is None:
                tiempo_taladro = 3

            muestras = list(igneas) + list(sedimentarias)
            tiempo_recolectar = muestras_restantes * 2
            tiempo_depositar = muestras_restantes 

            for m in muestras:
                distancia = self.manhattan(posicion, m)
                distancias.append(distancia)
            
            tiempo = max(distancias) * 0.5 + tiempo_recolectar + tiempo_depositar + tiempo_taladro
        
        return tiempo

def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):

    problema = ProblemaRover(
        rover_inicio=rover_inicio,
        bateria_inicial=bateria_inicial,
        zonas_sombra=zonas_sombra,
        muestras_igneas=muestras_igneas,
        muestras_sedimentarias=muestras_sedimentarias,
    )

    result = astar(problema, graph_search=True)

    if result is None:
        return "No se encontró solución"
    
    return [accion for accion, _ in result.path() if accion is not None]