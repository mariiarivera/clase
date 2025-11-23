# se uso inteligencia artifical para poner comentarios en el codigo y cuando salian errores que no entendia
# ============================================================
# Archivo: agent2.py
# Descripción: Define el comportamiento de múltiples agentes tipo
#              Roomba que colaboran sin comunicación explícita,
#              evitando choques, compartiendo estaciones y
#              gestionando energía en un entorno discreto.
# Autor: [TU NOMBRE] - [TU MATRÍCULA]
# Fecha de modificación: 22/11/2025
# ============================================================

from mesa.discrete_space import CellAgent, FixedAgent
from collections import deque


class RandomAgent(CellAgent):
    """
    Roomba reactiva utilizada en el modelo multi-agente.
    Evita colisiones, gestiona batería y comparte información
    de estaciones de carga detectadas.
    """

    def __init__(self, model, cell):
        """
        Inicializa una Roomba dentro del grid.

        Parámetros:
            model: referencia al modelo principal.
            cell: celda donde se colocará inicialmente.

        Retorno:
            Ninguno.
        """
        super().__init__(model)
        self.model = model
        self.cell = cell
        self.cell.agents.append(self)
        self.battery = 100
        self.movements = 0
        self.path = []
        self.state = "search_dirty"
        self.charging_station = cell  # primera estación detectada

        # Registrar estación inicial en memoria global compartida
        self.model.known_stations.add(cell)

    def recharge(self):
        """
        Recarga la batería del agente si está sobre una estación.

        Parámetros:
            Ninguno.

        Retorno:
            Ninguno. Actualiza self.battery.
        """
        if any(isinstance(a, ChargingStation) for a in self.cell.agents):
            self.battery = min(100, self.battery + 5)
            # Asegura que todos los agentes conozcan esta estación
            self.model.known_stations.add(self.cell)

    def needs_charge(self):
        """
        Determina si la batería es insuficiente para
        alcanzar la estación más cercana.

        Parámetros:
            Ninguno.

        Retorno:
            True si necesita cargar, False de lo contrario.
        """
        distance = self.bfs_distance_to_nearest_station()
        return self.battery < distance + 1

    def bfs_distance_to_nearest_station(self):
        """
        Calcula la distancia BFS hacia la estación más cercana
        conocida por el sistema multi-agente.

        Parámetros:
            Ninguno.

        Retorno:
            Distancia mínima en pasos.
        """
        queue = deque([(self.cell, 0)])
        visited = {self.cell}

        while queue:
            current, dist = queue.popleft()

            if current in self.model.known_stations:
                return dist

            neighbors = current.neighborhood.select(
                lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents) and
                          all(not isinstance(a, RandomAgent) for a in c.agents)
            )

            for n in neighbors:
                if n not in visited:
                    visited.add(n)
                    queue.append((n, dist + 1))

        return float('inf')

    def find_path_to_station(self):
        """
        Calcula ruta BFS hacia la estación más cercana.

        Parámetros:
            Ninguno.

        Retorno:
            Lista de celdas formando el camino.
        """
        queue = deque([(self.cell, [self.cell])])
        visited = {self.cell}

        while queue:
            current, path = queue.popleft()

            if current in self.model.known_stations:
                return path[1:]  # excluye celda actual

            neighbors = current.neighborhood.select(
                lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents) and
                          all(not isinstance(a, RandomAgent) for a in c.agents)
            )

            for n in neighbors:
                if n not in visited:
                    visited.add(n)
                    queue.append((n, path + [n]))

        return []

    def find_nearest_dirty_bfs(self):
        """
        Busca mediante BFS la celda sucia más cercana,
        evitando obstáculos y otros agentes.

        Parámetros:
            Ninguno.

        Retorno:
            Camino hacia la suciedad o lista vacía.
        """
        queue = deque([(self.cell, [self.cell])])
        visited = {self.cell}

        while queue:
            current, path = queue.popleft()

            if any(isinstance(a, DirtyCell) for a in current.agents):
                return path[1:]

            neighbors = current.neighborhood.select(
                lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents) and
                          all(not isinstance(a, RandomAgent) for a in c.agents)
            )

            for n in neighbors:
                if n not in visited:
                    visited.add(n)
                    queue.append((n, path + [n]))

        return []

    def move_along_path(self):
        """
        Avanza un paso a lo largo del camino calculado.

        Parámetros:
            Ninguno.

        Retorno:
            Ninguno.
        """
        if self.path:
            next_cell = self.path[0]

            # Prevenir colisión entre Roombas
            if not any(isinstance(a, RandomAgent) for a in next_cell.agents):
                self.cell.agents.remove(self)
                self.cell = next_cell
                self.cell.agents.append(self)
                self.path.pop(0)
                self.movements += 1
                self.battery = max(0, self.battery - 1)

    def clean(self):
        """
        Elimina suciedad en su celda actual si existe.

        Parámetros:
            Ninguno.

        Retorno:
            Ninguno.
        """
        dirt = next((a for a in self.cell.agents if isinstance(a, DirtyCell)), None)

        if dirt:
            dirt.remove()
            self.battery = max(0, self.battery - 1)
            self.path = []

    def step(self):
        """
        Ejecuta una acción del ciclo de vida del agente:
        carga, búsqueda de estación, exploración, movimiento y limpieza.

        Parámetros:
            Ninguno.

        Retorno:
            Ninguno.
        """

        # Intentar cargar batería si está sobre estación
        self.recharge()

        # Si requiere carga → navegar hacia estación más cercana
        if self.needs_charge():
            self.state = "go_charge"

            if not self.path:
                self.path = self.find_path_to_station()

        # Si no requiere carga → buscar suciedad
        else:
            self.state = "search_dirty"

            if not self.path:
                self.path = self.find_nearest_dirty_bfs()

        # Ejecutar movimiento
        self.move_along_path()

        # Limpiar en caso de encontrar suciedad
        self.clean()


# ============================================================
# Clases auxiliares del ambiente (celdas fijas)
# ============================================================

class DirtyCell(FixedAgent):
    """
    Representa una celda sucia dentro del ambiente.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        cell.agents.append(self)

    def step(self):
        """No realiza acciones activas."""
        pass


class ObstacleAgent(FixedAgent):
    """
    Representa un obstáculo fijo dentro de la cuadrícula.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        cell.agents.append(self)

    def step(self):
        """No realiza acciones activas."""
        pass


class ChargingStation(FixedAgent):
    """
    Punto de recarga para los agentes Roomba.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        cell.agents.append(self)

    def step(self):
        """No realiza acciones activas."""
        pass
