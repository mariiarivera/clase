# se uso inteligencia artifical para poner comentarios en el codigo y cuando salian errores que no entendia
# ============================================================
# Archivo: app2.py
# Descripción: Configura la interfaz gráfica para la simulación 
#              multi-agente utilizando SolaraViz. Visualiza el
#              grid, los agentes, las estadísticas de limpieza,
#              la batería de cada Roomba y los steps ejecutados.
# Autor: [TU NOMBRE] - [TU MATRICULA]
# Fecha de modificación: 22/11/2025
# ============================================================

# ----------------- Imports -----------------
from mesa.visualization import Slider, SolaraViz, make_space_component, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle
from random_agents.agent import RandomAgent, ObstacleAgent, DirtyCell, ChargingStation
from random_agents.model import RandomModel


# ----------------- Portrayal de agentes -----------------
def random_portrayal(agent):
    """
    Define cómo se muestra cada agente dentro del grid
    dependiendo de su tipo (Roomba, obstáculo, suciedad, estación).

    Parámetros:
        agent: instancia individual del agente a representar.

    Retorno:
        Objeto AgentPortrayalStyle configurado con forma, color y tamaño.
    """
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(size=50, marker="o")

    if isinstance(agent, RandomAgent):
        portrayal.color = "blue"

    elif isinstance(agent, ObstacleAgent):
        portrayal.color = "gray"
        portrayal.marker = "s"
        portrayal.size = 100

    elif isinstance(agent, DirtyCell):
        portrayal.color = "black"

    elif isinstance(agent, ChargingStation):
        portrayal.color = "green"
        portrayal.marker = "s"
        portrayal.size = 100

    return portrayal


def post_process(ax):
    """
    Ajusta el aspecto del grid para que cada celda sea cuadrada.

    Parámetros:
        ax: eje de Matplotlib encargado de la visualización.

    Retorno:
        Ninguno.
    """
    ax.set_aspect("equal")


# ----------------- Parámetros del modelo -----------------
model_params = {
    "seed": {"type": "InputText", "value": 42, "label": "Random Seed"},
    "width": Slider("Grid width", 28, 1, 50),
    "height": Slider("Grid height", 28, 1, 50),
    "num_agents": Slider("Number of Roombas", 10, 1, 10),
    "dirty_percent": Slider("Dirty cells %", 0.2, 0.0, 1.0, 0.05),
    "obstacle_percent": Slider("Obstacle %", 0.1, 0.0, 0.5, 0.05),
}


# ----------------- Inicializar modelo -----------------
model = RandomModel(
    width=model_params["width"].value,
    height=model_params["height"].value,
    seed=model_params["seed"]["value"],
    num_agents=model_params["num_agents"].value,
    dirty_percent=model_params["dirty_percent"].value,
    obstacle_percent=model_params["obstacle_percent"].value
)


# ----------------- Grid -----------------
space_component = make_space_component(
    random_portrayal,
    draw_grid=True,     # Permite visualizar las celdas del grid
    post_process=post_process
)


# ----------------- Graficas -----------------

# Cantidad de celdas sucias durante el tiempo
dirty_count_plot = make_plot_component({"DirtyCells": "black"})

# Colores automáticos para cada Roomba: C0, C1, C2...
roomba_colors = {f"Roomba_{i}_Battery": f"C{i}" for i in range(model.num_agents)}

# Gráfica del nivel de batería de cada agente
battery_plot = make_plot_component(roomba_colors)

# Gráfica del número total de steps ejecutados
steps_plot = make_plot_component({"Steps": "green"})

# Porcentaje de limpieza acumulada
cleaned_plot = make_plot_component({"CleanedPercentage": "orange"})


# ----------------- Crear la app -----------------
page = SolaraViz(
    model,
    components=[
        space_component,
        dirty_count_plot,
        battery_plot,
        steps_plot,
        cleaned_plot
    ],
    model_params=model_params,
    name="Roomba Cleaning Simulation",
)
