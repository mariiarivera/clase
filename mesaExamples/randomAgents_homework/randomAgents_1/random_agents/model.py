# se uso inteligencia artifical para poner comentarios en el codigo y cuando salian errores que no entendia
# ============================================================
# Archivo: model.py
# Descripción: Define la estructura del modelo para la simulación
#              de un agente Roomba. Configura el grid, obstáculos,
#              celdas sucias, estación de carga y el DataCollector.
# Autor: [TU NOMBRE] - [TU MATRÍCULA]
# Fecha de modificación: 22/11/2025
# ============================================================

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import RandomAgent, ObstacleAgent, DirtyCell, ChargingStation


class RandomModel(Model):
    """
    Modelo principal de la simulación. Se encarga de inicializar el ambiente,
    colocar agentes, definir celdas sucias, obstáculos y manejar la
    recolección de datos durante cada step.
    """

    def __init__(self, width=8, height=8, dirty_percent=0.2, seed=42, obstacle_percent=0.1):
        """
        Inicializa el modelo de la simulación.

        Parámetros:
            width: ancho del grid.
            height: altura del grid.
            dirty_percent: porcentaje de celdas que iniciarán sucias.
            seed: semilla para generación aleatoria reproducible.
            obstacle_percent: porcentaje de celdas internas que serán obstáculos.

        Valor de retorno:
            Ninguno.
        """
        super().__init__(seed=seed)

        self.width = width
        self.height = height
        self.dirty_percent = dirty_percent
        self.obstacle_percent = obstacle_percent
        self.steps_count = 0  # Contador total de pasos ejecutados

        # Grid con vecindad Moore (8 direcciones) y sin toroidal
        self.grid = OrthogonalMooreGrid(
            [self.width, self.height],
            torus=False,
            random=self.random
        )

        # -------------------------------------------------------
        # Construcción del borde del mapa como obstáculos fijos
        # -------------------------------------------------------
        border = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1
        ]

        # Creamos obstáculos en todas las celdas marcadas como borde
        for cell in self.grid.all_cells:
            if cell.coordinate in border:
                ObstacleAgent(self, cell)

        # -------------------------------------------------------
        # Colocar estación de carga fija en (1, 1)
        # -------------------------------------------------------
        charging_cell = self.grid[1, 1]
        ChargingStation(self, charging_cell)

        # -------------------------------------------------------
        # Crear la Roomba principal en la estación de carga
        # -------------------------------------------------------
        self.roomba = RandomAgent(self, charging_cell)

        # -------------------------------------------------------
        # Determinar celdas internas disponibles para suciedad
        # -------------------------------------------------------
        available_cells = [
            cell
            for cell in self.grid.empties
            if cell.coordinate != (1, 1) and cell.coordinate not in border
        ]

        # -------------------------------------------------------
        # Crear celdas sucias según porcentaje seleccionado
        # -------------------------------------------------------
        num_dirty = int(len(available_cells) * self.dirty_percent)
        dirty_cells = self.random.sample(available_cells, k=num_dirty)
        DirtyCell.create_agents(self, num_dirty, dirty_cells)

        self.initial_dirty = num_dirty

        # Actualizamos lista de celdas disponibles quitando las sucias
        available_cells = [c for c in available_cells if c not in dirty_cells]

        # -------------------------------------------------------
        # Crear obstáculos internos según porcentaje indicado
        # -------------------------------------------------------
        num_obstacles = int(len(available_cells) * self.obstacle_percent)
        obstacle_cells = self.random.sample(available_cells, k=num_obstacles)
        ObstacleAgent.create_agents(self, num_obstacles, obstacle_cells)

        # -------------------------------------------------------
        # Configuración del DataCollector
        # -------------------------------------------------------
        self.datacollector = DataCollector({
            "DirtyCells": lambda m: len(m.agents_by_type[DirtyCell]),
            "RoombaBattery": lambda m: m.roomba.battery,
            "Steps": lambda m: m.steps_count,
        })

        self.running = True

        # Registrar datos iniciales
        self.datacollector.collect(self)

    def step(self):
        """
        Ejecuta un ciclo de simulación.
        Realiza la acción de cada agente, incrementa
        el contador de pasos y registra estadísticas.

        Parámetros:
            Ninguno.

        Valor de retorno:
            Ninguno.
        """
        self.agents.shuffle_do("step")
        self.steps_count += 1
        self.datacollector.collect(self)
