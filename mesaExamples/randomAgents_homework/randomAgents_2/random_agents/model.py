# se uso inteligencia artifical para poner comentarios en el codigo y cuando salian errores que no entendia
# ============================================================
# Archivo: model2.py
# Descripción: Modelo multi-agente para simular múltiples Roombas
#              trabajando simultáneamente. Administra el grid, la 
#              creación de estaciones, obstáculos, celdas sucias
#              y agentes. También gestiona las estadísticas y el 
#              control de la simulación en el tiempo.
# Autor: [TU NOMBRE] - [TU MATRÍCULA]
# Fecha de modificación: 22/11/2025
# ============================================================

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import RandomAgent, ObstacleAgent, DirtyCell, ChargingStation


class RandomModel(Model):
    """
    Modelo para múltiples Roombas que colaboran mediante 
    comportamiento reactivo. Cada agente detecta suciedad,
    navega evitando colisiones y comparte estaciones de carga.
    """

    def __init__(
        self,
        width=8,
        height=8,
        dirty_percent=0.2,
        obstacle_percent=0.1,
        seed=42,
        num_agents=10,
        max_steps=500
    ):
        """
        Inicializa todos los componentes del modelo multi-agente.

        Parámetros:
            width: ancho del grid.
            height: alto del grid.
            dirty_percent: porcentaje del ambiente que inicia sucio.
            obstacle_percent: porcentaje de obstáculos internos.
            seed: semilla para la aleatoriedad del modelo.
            num_agents: número de Roombas a simular.
            max_steps: número máximo de steps antes de detener.
        
        Retorno:
            Ninguno.
        """
        super().__init__(seed=seed)

        self.width = width
        self.height = height
        self.dirty_percent = dirty_percent
        self.obstacle_percent = obstacle_percent
        self.num_agents = num_agents
        self.steps_count = 0
        self.max_steps = max_steps
        self.running = True

        # Memoria compartida entre agentes para registrar estaciones
        self.known_stations = set()

        # ------------------------------------------------------------
        # Construcción del grid sin toroidal y con vecindad Moore
        # ------------------------------------------------------------
        self.grid = OrthogonalMooreGrid(
            [self.width, self.height],
            torus=False,
            random=self.random
        )

        # ------------------------------------------------------------
        # Crear borde de obstáculos alrededor del grid
        # ------------------------------------------------------------
        border = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1
        ]

        for cell in self.grid.all_cells:
            if cell.coordinate in border:
                ObstacleAgent(self, cell)

        # ------------------------------------------------------------
        # Crear Roombas y una estación de carga en su celda inicial
        # ------------------------------------------------------------
        self.roombas = []
        available_cells = [
            c for c in self.grid.empties
            if not c.agents and c.coordinate not in border
        ]

        if len(available_cells) < self.num_agents:
            raise ValueError("No hay suficientes celdas vacías para colocar todos los Roombas")

        for _ in range(self.num_agents):
            start_cell = self.random.choice(available_cells)
            available_cells.remove(start_cell)

            # Crear estación de carga en su posición inicial
            ChargingStation(self, start_cell)
            self.known_stations.add(start_cell)

            # Crear Roomba y registrar su estación principal
            agent = RandomAgent(self, start_cell)
            agent.charging_station = start_cell
            self.roombas.append(agent)

        # ------------------------------------------------------------
        # Crear celdas sucias según porcentaje indicado
        # ------------------------------------------------------------
        available_cells = [
            c for c in self.grid.empties
            if not c.agents and c.coordinate not in border
        ]

        num_dirty = int(len(available_cells) * self.dirty_percent)
        dirty_cells = self.random.sample(available_cells, k=num_dirty)

        DirtyCell.create_agents(self, num_dirty, dirty_cells)
        self.initial_dirty = num_dirty

        # ------------------------------------------------------------
        # Crear obstáculos internos en espacios vacíos restantes
        # ------------------------------------------------------------
        available_cells = [
            c for c in self.grid.empties
            if not c.agents and c.coordinate not in border
        ]

        num_obstacles = int(len(available_cells) * self.obstacle_percent)
        obstacle_cells = self.random.sample(available_cells, k=num_obstacles)

        ObstacleAgent.create_agents(self, num_obstacles, obstacle_cells)

        # ------------------------------------------------------------
        # Recolector de estadísticas para gráficas
        # ------------------------------------------------------------
        self.datacollector = DataCollector({
            "DirtyCells": lambda m: len([
                a for cell in m.grid.all_cells 
                for a in cell.agents 
                if isinstance(a, DirtyCell)
            ]),
            **{
                f"Roomba_{i}_Battery": (lambda m, i=i: m.roombas[i].battery)
                for i in range(self.num_agents)
            },
            "Steps": lambda m: m.steps_count,
            "CleanedPercentage": lambda m: (
                (m.initial_dirty - len([
                    a for cell in m.grid.all_cells 
                    for a in cell.agents 
                    if isinstance(a, DirtyCell)
                ])) / m.initial_dirty * 100
                if m.initial_dirty > 0
                else 0
            )
        })

        # Registrar datos iniciales
        self.datacollector.collect(self)

    def step(self):
        """
        Ejecuta un ciclo de simulación. Detiene el modelo si se 
        alcanza el máximo de steps, o si no hay más suciedad que limpiar.
        
        Parámetros:
            Ninguno.

        Retorno:
            Ninguno.
        """
        if self.steps_count >= self.max_steps:
            self.running = False
            return

        self.agents.shuffle_do("step")
        self.steps_count += 1
        self.datacollector.collect(self)
