from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid

from .agent import Roomba, Furniture, dirtyBlock

class RandomModel(Model):
    """
    Creates a new model with random agents.
    Args:
        num_agents: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, num_agents=10, width=8, height=8, seed=42):

        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.seed = seed
        self.width = width
        self.height = height

        self.grid = OrthogonalMooreGrid([width, height], torus=False)

        # Identify the coordinates of the border of the grid
        border = [(x,y)
                  for y in range(height)
                  for x in range(width)
                  if y in [0, height-1] or x in [0, width - 1]]

        # Place furniture and dirty blocks in random positions
        total_cells = self.grid.num_cells
        total_furniture = total_cells // 10
        total_dirty = total_cells // 10

        for _ in range(total_furniture):
            cell = self.random.choice(self.grid.empties.cells)
            Furniture.create_agents(self, 1, cell=[cell])


        Roomba.create_agents(
            self,
            self.num_agents,
            cell=self.random.choices(self.grid.empties.cells, k=self.num_agents)
        )

        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        self.agents.shuffle_do("step")
