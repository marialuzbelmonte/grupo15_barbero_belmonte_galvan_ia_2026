from simpleai.search import SearchProblem, astar

class AresRoverProblem(SearchProblem):
    def _init_(self, rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
        # El estado inicial
        estado_inicial = (
            rover_inicio,                     # (fila, columna)
            bateria_inicial,                  # int (max 20)
            None,                             # taladro activo: None, "termico" o "percusión"
            frozenset(),                      # muestras en la bodega (guardamos sus posiciones originales)
            frozenset(muestras_igneas),       # posiciones de ígneas que faltan recolectar
            frozenset(muestras_sedimentarias) # posiciones de sedimentarias que faltan recolectar
        )

        super()._init_(initial_state=estado_inicial)
        self.zonas_sombra = set(zonas_sombra)

    def actions(self, state):
        pos, bat, taladro, carga, igneas, sedimentarias = state
        r, c = pos
        actions_list = []

        # Si el rover se quedó sin batería (<= 0), no puede hacer nada (estado fallido)
        if bat <= 0:
            return actions_list

        # --- Acción: DESPLEGAR PANELES SOLARES (recargar) ---
        if pos not in self.zonas_sombra and bat < 20:
            actions_list.append(("recargar", None))

        # --- Acción: EQUIPAR TALADRO ---
        if taladro != "termico":
            actions_list.append(("equipar", "termico"))
        if taladro != "percusión":
            actions_list.append(("equipar", "percusión"))

        # --- Acción: PERFORAR Y RECOLECTAR ---
        if len(carga) < 2:
            if pos in igneas and taladro == "termico":
                actions_list.append(("recolectar", "ignea"))
            if pos in sedimentarias and taladro == "percusión":
                actions_list.append(("recolectar", "sedimentaria"))

        # --- Acción: DEPOSITAR CÁPSULA ---
        if len(carga) > 0:
            # Condición: Debe tener 2 muestras, a menos que sean las últimas que quedaban en todo el mapa
            muestras_restantes_en_mapa = len(igneas) + len(sedimentarias)
            if len(carga) == 2 or (muestras_restantes_en_mapa == 0):
                actions_list.append(("depositar", None))

        # --- Acciones de Movimiento: MOVERSE y SOBREMARCHA ---
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Arriba, Abajo, Izquierda, Derecha

        for dr, dc in direcciones:
            # Moverse 1 celda
            actions_list.append(("moverse", (r + dr, c + dc)))
            # Sobremarcha (2 celdas en línea recta)
            actions_list.append(("sobremarcha", (r + 2 * dr, c + 2 * dc)))

        return actions_list

    def result(self, state, action):
        pos, bat, taladro, carga, igneas, sedimentarias = state
        tipo, param = action

        # Copiamos las estructuras mutables para el nuevo estado
        nuevo_pos = pos
        nueva_bat = bat
        nuevo_taladro = taladro
        nueva_carga = set(carga)
        nuevas_igneas = set(igneas)
        nuevas_sedimentarias = set(sedimentarias)

        if tipo == "recargar":
            nueva_bat = min(20, bat + 10)
        
        elif tipo == "equipar":
            nuevo_taladro = param
            nueva_bat -= 1
            
        elif tipo == "recolectar":
            # Guardamos la posición actual como identificador de la muestra en la bodega
            nueva_carga.add(pos)
            if param == "ignea":
                nuevas_igneas.remove(pos)
            else:
                nuevas_sedimentarias.remove(pos)
            nueva_bat -= 3

        elif tipo == "depositar":
            nueva_carga.clear()
            # El enunciado dice: 1 minuto por muestra entregada, consume 1 unidad de batería en TOTAL por la acción.
            nueva_bat -= 1

        elif tipo == "moverse":
            nuevo_pos = param
            nueva_bat -= 1

        elif tipo == "sobremarcha":
            nuevo_pos = param
            nueva_bat -= 4

        return (nuevo_pos, nueva_bat, nuevo_taladro, frozenset(nueva_carga), frozenset(nuevas_igneas), frozenset(nuevas_sedimentarias))

    def cost(self, state, action, state2):
        # El costo está medido en MINUTOS
        tipo, param = action
        if tipo == "moverse":
            return 1
        elif tipo == "sobremarcha":
            return 1
        elif tipo == "equipar":
            return 3
        elif tipo == "recolectar":
            return 2
        elif tipo == "depositar":
            # 1 minuto por cada muestra que tuviera cargada en el estado anterior
            # state[3] es la carga del estado previo
            return len(state[3])
        elif tipo == "recargar":
            return 4
        return 0

    def is_goal(self, state):
        pos, bat, taladro, carga, igneas, sedimentarias = state
        # El objetivo se cumple si no quedan muestras en el mapa, la bodega está vacía y el rover sigue activo
        return len(igneas) == 0 and len(sedimentarias) == 0 and len(carga) == 0 and bat > 0

    def heuristic(self, state):
        pos, bat, taladro, carga, igneas, sedimentarias = state
        
        # Si la batería murió, este camino es inválido. Retornamos un costo infinito simulado.
        if bat <= 0:
            return float('inf')

        # Cantidad de muestras que faltan procesar por completo
        muestras_restantes = len(igneas) + len(sedimentarias)
        muestras_en_bodega = len(carga)

        if muestras_restantes == 0 and muestras_en_bodega == 0:
            return 0

        # Heurística Admisible (Subestima el costo real):
        # Cada muestra en el mapa requerirá obligatoriamente: 1 acción de recolectar (2 min)
        # Cada muestra recolectada o por recolectar requerirá ser depositada (1 min por muestra)
        costo_minimo_acciones = (muestras_restantes * 2) + ((muestras_restantes + muestras_en_bodega) * 1)
        
        return costo_minimo_acciones
    
def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    # Instanciar el problema de búsqueda tradicional
    problema = AresRoverProblem(
        rover_inicio=rover_inicio,
        bateria_inicial=bateria_inicial,
        zonas_sombra=zonas_sombra,
        muestras_igneas=muestras_igneas,
        muestras_sedimentarias=muestras_sedimentarias
    )
    
    # Resolver usando A* (A-Star) para garantizar el camino de menor tiempo (óptimo)
    resultado = astar(problema, graph_search=True)
    
    # Si encuentra solución, extrae la lista de acciones de los bordes del árbol de búsqueda
    if resultado:
        plan = []
        for accion, nuevo_estado in resultado.path():
            if accion is not None:
                # Modificación cosmética de "depositar": el enunciado pide el texto ("depositar", None)
                # pero el ejemplo de salida del enunciado mostró ("depositar", None) en la descripción
                # y un comentario aclarando: Ejemplo: ("entregar", None). 
                # Ajustamos el string al tipo de acción solicitado ("depositar")
                plan.append(accion)
        return plan
    else:
        return []