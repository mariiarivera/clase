# se uso inteligencia artifical para poner comentarios en el codigo y cuando salian erroes que no entendia 
# ============================================================
# Archivo: agent.py
# Descripción: Define los agentes utilizados en la simulación:
#              Roomba (RandomAgent), DirtyCell, ObstacleAgent
#              y ChargingStation. Implementa la lógica de
#              percepción, movimiento, limpieza y carga.
# Autor: [TU NOMBRE] - [TU MATRÍCULA]
# Fecha de modificación: 22/11/2025
# ============================================================

from mesa.discrete_space import CellAgent, FixedAgent
from collections import deque


class RandomAgent(CellAgent):
    """
    Clase que representa a la Roomba en la simulación.
    El agente puede moverse, limpiar, buscar suciedad,
    navegar hacia la estación de carga y gestionar su batería.
    """

    def __init__(self, model, cell):
        """
        Inicializa un agente Roomba.

        Parámetros:
            model: instancia del modelo principal.
            cell: celda inicial en la que se coloca el agente.

        Valor de retorno:
            Ninguno.
        """
        super().__init__(model)
        self.cell = cell
        self.battery = 100
        self.movements = 0
        self.path = []               
        self.charging_station = None 
        self.state = "search_dirty"

        # Identificación inicial de la estación de carga
        self.find_charging_station()

    def find_charging_station(self):
        """
        Busca dentro del grid la celda que contiene la estación de carga.

        Parámetros:
            Ninguno.

        Valor de retorno:
            Ninguno. Actualiza self.charging_station.
        """
        for cell in self.model.grid.all_cells:
            if any(isinstance(a, ChargingStation) for a in cell.agents):
                self.charging_station = cell
                return

    def recharge(self):
        """
        Incrementa la batería del agente cuando se encuentra sobre
        la estación de carga.

        Parámetros:
            Ninguno.

        Valor de retorno:
            Ninguno. Modifica el nivel de batería.
        """
        if any(isinstance(a, ChargingStation) for a in self.cell.agents):
            self.battery = min(100, self.battery + 25)
            self.state = "charging"

    def needs_charge(self):
        """
        Determina si la batería actual es insuficiente
        para regresar a la estación de carga.

        Parámetros:
            Ninguno.

        Valor de retorno:
            True si requiere cargar, False en caso contrario.
        """
        if not self.charging_station:
            return self.battery < 30
        
        distance = self.bfs_distance(self.cell, self.charging_station)
        return self.battery < (distance + 10)

    def bfs_distance(self, start, goal):
        """
        Calcula la distancia BFS entre dos celdas del grid,
        evitando obstáculos.

        Parámetros:
            start: celda inicial.
            goal: celda objetivo.

        Valor de retorno:
            Número entero con la distancia BFS o infinito si no existe camino.
        """
        if start == goal:
            return 0
        
        queue = deque([(start, 0)])
        visited = {start}
        
        while queue:
            current, distance = queue.popleft()
            
            if current == goal:
                return distance
            
            neighbors = current.neighborhood.select(
                lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents)
            )
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))
        
        return float('inf')

    def find_nearest_dirty_bfs(self):
        """
        Realiza BFS para encontrar la celda sucia más cercana.

        Parámetros:
            Ninguno.

        Valor de retorno:
            Lista con el camino hacia la celda sucia o lista vacía.
        """
        queue = deque([(self.cell, [self.cell])])
        visited = {self.cell}
        
        while queue:
            current, path = queue.popleft()
            
            if any(isinstance(a, DirtyCell) for a in current.agents):
                return path[1:]
            
            neighbors = current.neighborhood.select(
                lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents)
            )
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []

    def find_path_to_charging_station(self):
        """
        Calcula ruta BFS hacia la estación de carga.

        Parámetros:
            Ninguno.

        Valor de retorno:
            Lista de celdas que representan el camino.
        """
        if not self.charging_station:
            return []
        
        queue = deque([(self.cell, [self.cell])])
        visited = {self.cell}
        
        while queue:
            current, path = queue.popleft()
            
            if current == self.charging_station:
                return path[1:]
            
            neighbors = current.neighborhood.select(
                lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents)
            )
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []

    def check_nearby_dirty(self):
        """
        Revisa si existe suciedad en celdas vecinas.

        Parámetros:
            Ninguno.

        Valor de retorno:
            La celda sucia cercana o None si no existe.
        """
        neighbors = self.cell.neighborhood.select(
            lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents)
        )
        
        for neighbor in neighbors:
            if any(isinstance(a, DirtyCell) for a in neighbor.agents):
                return neighbor
        return None

    def move_along_path(self):
        """
        Avanza un paso siguiendo la ruta calculada.

        Parámetros:
            Ninguno.

        Valor de retorno:
            True si avanzó, False en caso contrario.
        """
        if self.path:
            next_cell = self.path.pop(0)
            self.cell = next_cell
            self.movements += 1
            self.battery -= 1
            return True
        return False

    def clean(self):
        """
        Limpia la suciedad presente en la celda actual.

        Parámetros:
            Ninguno.

        Valor de retorno:
            True si limpió, False en caso contrario.
        """
        dirt = next((a for a in self.cell.agents if isinstance(a, DirtyCell)), None)
        if dirt:
            dirt.remove()
            self.battery -= 1
            self.path = []
            self.state = "search_dirty"
            return True
        return False

    def step(self):
        """
        Actualiza el comportamiento del agente en cada ciclo:
        carga, movimiento, búsqueda y limpieza.

        Parámetros:
            Ninguno.

        Valor de retorno:
            Ninguno.
        """

        # ----------- Manejo de carga -----------
        if any(isinstance(a, ChargingStation) for a in self.cell.agents):

            if self.battery < 100:
                self.state = "charging"
                self.recharge()
                return  

            else:
                self.state = "search_dirty"

        # ----------- Verificar muerte por batería -----------
        if self.battery <= 0:
            self.state = "dead"
            return

        # ----------- Búsqueda de suciedad cercana -----------
        nearby_dirty = self.check_nearby_dirty()
        if nearby_dirty and not self.needs_charge():
            self.state = "search_dirty"
            self.path = [nearby_dirty]

        # ----------- Necesidad de carga -----------
        if self.needs_charge() and not any(isinstance(a, ChargingStation) for a in self.cell.agents):
            if not self.path:
                self.path = self.find_path_to_charging_station()
            self.state = "go_charge"

        # ----------- Búsqueda de suciedad (BFS) -----------
        if not self.path and not self.needs_charge():
            self.state = "search_dirty"
            self.path = self.find_nearest_dirty_bfs()

        # ----------- Movimiento y limpieza -----------
        self.move_along_path()
        self.clean()


class DirtyCell(FixedAgent):
    """
    Representa una celda sucia que puede ser eliminada por la Roomba.
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
    Representa un obstáculo fijo dentro del grid.
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
    Representa la estación de carga utilizada por la Roomba.
    """

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        cell.agents.append(self)

    def step(self):
        """No realiza acciones activas."""
        pass
