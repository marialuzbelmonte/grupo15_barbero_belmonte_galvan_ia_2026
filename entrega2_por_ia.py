from simpleai.search import CspProblem, backtrack

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    rows, cols = camp_size
    crater_set = set(craters)

    # 1. Definir las variables: todas las celdas de la cuadrícula
    variables = [(r, c) for r in range(rows) for c in range(cols)]

    # 2. Definir los dominios
    # Si es un cráter, no puede contener ningún módulo (dominio vacío o solo 'crater')
    # Para simplificar la lógica de "celda libre", usamos 'empty' para pasillos y 'crater' para obstáculos.
    domains = {}
    for var in variables:
        if var in crater_set:
            domains[var] = ['crater']
        else:
            domains[var] = ['hab', 'gen', 'lab', 'dep', 'air', 'empty']

    # --- FUNCIONES DE RESTRICCIÓN ---

    # Restricción 3 y 4: Posición en los bordes o interior
    def border_and_interior_constraints(variables_list, values_list):
        # Esta función evalúa una sola celda a la vez (Unaria)
        cell = variables_list[0]
        val = values_list[0]
        r, c = cell
        is_border = (r == 0 or r == rows - 1 or c == 0 or c == cols - 1)
        
        if val == 'air' and not is_border:
            return False  # Esclusas solo en el borde
        if val == 'hab' and is_border:
            return False  # Habitacionales solo en el interior
        return True

    # Restricción 5, 6, 7 y 8: Relaciones de adyacencia
    # Evaluamos pares de celdas vecinas para optimizar el backtracking de forma temprana
    def adjacency_constraints(variables_list, values_list):
        cell1, cell2 = variables_list
        val1, val2 = values_list

        # Regla 5: Seguridad energética (gen no adyacente a hab)
        if (val1 == 'gen' and val2 == 'hab') or (val1 == 'hab' and val2 == 'gen'):
            return False
        
        # Regla 6: Aislamiento entre generadores (gen no adyacente a gen)
        if val1 == 'gen' and val2 == 'gen':
            return False

        return True

    # Restricciones globales: Cantidad exacta de módulos requeridos
    def global_counts_constraint(variables_list, values_list):
        counts = {'hab': 0, 'gen': 0, 'lab': 0, 'dep': 0, 'air': 0}
        for val in values_list:
            if val in counts:
                counts[val] += 1
        
        return (counts['hab'] == habs and 
                counts['gen'] == generators and 
                counts['lab'] == labs and 
                counts['dep'] == deposits and 
                counts['air'] == airlocks)

    # Restricciones complejas de vecindad (Laboratorios y Evacuación)
    # Se ejecutan al final o sobre todo el mapa para garantizar el cumplimiento de todo el entorno
    def global_proximity_constraints(variables_list, values_list):
        # Creamos un mapa rápido de la asignación actual
        assignment = dict(zip(variables_list, values_list))
        
        for (r, c), val in assignment.items():
            # Obtener vecinos ortogonales válidos
            neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    neighbors.append((nr, nc))

            # Regla 7: Cadena de suministro científico (lab adyacente a al menos un dep)
            if val == 'lab':
                has_deposit = any(assignment[n] == 'dep' for n in neighbors)
                if not has_deposit:
                    return False

            # Regla 8: Ruta de evacuación (hab adyacente a al menos una celda libre/empty)
            if val == 'hab':
                has_escape = any(assignment[n] == 'empty' for n in neighbors)
                if not has_escape:
                    return False
                    
        return True

    # --- AGREGAR RESTRICCIONES AL CSP ---
    constraints = []

    # Añadir restricciones unarias (Bordes e Interior)
    for var in variables:
        constraints.append(((var,), border_and_interior_constraints))

    # Añadir restricciones binarias de adyacencia (Para adelantar podas en el árbol)
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            r1, c1 = variables[i]
            r2, c2 = variables[j]
            if abs(r1 - r2) + abs(c1 - c2) == 1:  # Si son vecinos ortogonales
                constraints.append(((variables[i], variables[j]), adjacency_constraints))

    # Restricciones globales (actúan sobre todas las variables del problema)
    constraints.append((tuple(variables), global_counts_constraint))
    constraints.append((tuple(variables), global_proximity_constraints))

    # 3. Resolver el problema mediante Backtracking
    problem = CspProblem(variables, domains, constraints)
    solution = backtrack(problem)

    # 4. Formatear la salida según el requerimiento de la interfaz
    if not solution:
        return None

    result = []
    for (r, c), val in solution.items():
        if val in ['hab', 'gen', 'lab', 'dep', 'air']:
            result.append((val, r, c))
            
    return result