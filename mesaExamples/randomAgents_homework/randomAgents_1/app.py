# se uso inteligencia artifical para poner comentarios en el codigo y cuando salian errores que no entendia
# ============================================================
# Archivo: app.py
# Descripción: Configura la visualización interactiva de la 
#              simulación. Define la apariencia de los agentes,
#              parámetros del modelo, gráficas y la interfaz
#              generada con SolaraViz.
# Autor: [TU NOMBRE] - [TU MATRÍCULA]
# Fecha de modificación: 22/11/2025
# ============================================================

from random_agents.agent import RandomAgent, ObstacleAgent, DirtyCell, ChargingStation
from random_agents.model import RandomModel

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
    make_plot_component,
)

from mesa.visualization.components import AgentPortrayalStyle


def random_portrayal(agent):
    """
    Determina cómo se muestra cada agente en la visualización.

    Parámetros:
        agent: instancia individual del agente a representar.

    Retorno:
        Objeto AgentPortrayalStyle configurado con color, tamaño
        y forma dependiendo del tipo de agente.
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
    Ajusta el aspecto del gráfico espacial al formato cuadrado.

    Parámetros:
        ax: objeto del eje de Matplotlib utilizado para dibujar.

    Retorno:
        Ninguno.
    """
    ax.set_aspect("equal")


# ------------------------------------------------------------
# Parámetros configurables para la simulación desde la interfaz
# ------------------------------------------------------------
model_params = {
    "seed": {"type": "InputText", "value": 42, "label": "Random Seed"},
    "width": Slider("Grid width", 28, 1, 50),
    "height": Slider("Grid height", 28, 1, 50),
}

# ------------------------------------------------------------
# Inicializar el modelo principal usando los parámetros elegidos
# ------------------------------------------------------------
model = RandomModel(
    width=model_params["width"].value,
    height=model_params["height"].value,
    seed=model_params["seed"]["value"]
)

# ------------------------------------------------------------
# Configuración de la visualización del espacio (grid)
# ------------------------------------------------------------
space_component = make_space_component(
    random_portrayal,
    draw_grid=False,
    post_process=post_process
)

# ------------------------------------------------------------
# Gráfica 1: Cantidad de DirtyCells en el tiempo
# ------------------------------------------------------------
dirty_count_plot = make_plot_component(
    {"DirtyCells": "black"}
)

# ------------------------------------------------------------
# Gráfica 2: Nivel de batería de la Roomba
# ------------------------------------------------------------
battery_plot = make_plot_component(
    {"RoombaBattery": "blue"}
)

# ------------------------------------------------------------
# Gráfica 3: Número de pasos ejecutados
# ------------------------------------------------------------
steps_plot = make_plot_component(
    {"Steps": "green"}
)

# ------------------------------------------------------------
# Empaquetar todo en la página interactiva de SolaraViz
# ------------------------------------------------------------
page = SolaraViz(
    model,
    components=[space_component, dirty_count_plot, battery_plot, steps_plot],
    model_params=model_params,
    name="Roomba Cleaning Simulation",
)
