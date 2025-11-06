# FixedAgent: Immobile agents permanently fixed to cells
from mesa.discrete_space import FixedAgent

class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    @property
    def x(self):
        return self.cell.coordinate[0]

    @property
    def y(self):
        return self.cell.coordinate[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.cell.neighborhood.agents
     

                

    
    def __init__(self, model, cell, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """
        # Get the neighbors and apply the rules on whether to be alive or dead
        # at the next tick.
        live_neighbors = sum(neighbor.is_alive for neighbor in self.neighbors)

        # Assume nextState is unchanged, unless changed below.
        self._next_state = self.state

        #here we add a list of the neighbors positions, but only the upper ones
        upLeft =[self.x - 1, self.y + 1]
        up = [self.x, self.y + 1]
        upRight = [self.x + 1, self.y + 1]

        #now we check the status of each neighbor
        upLeftStatus = False
        upStatus = False
        upRightStatus = False

        #loop through neighbors to find their status
        for neighbor in self.neighbors:
            neighbor_pos = [neighbor.x, neighbor.y]
    
            if neighbor_pos == upLeft and neighbor.is_alive:
                upLeftStatus = True
            if neighbor_pos == up and neighbor.is_alive:    
                upStatus = True
            if neighbor_pos == upRight and neighbor.is_alive:
                upRightStatus = True

        #now we apply the rules based on the status of the upper neighbors, starting from the upper row and making sure the status are changing
        if(self.y == 49):
            self._next_state = self.state
        elif upLeftStatus and upStatus and upRightStatus:
            self._next_state = self.DEAD
        elif upLeftStatus and upStatus and not upRightStatus:
            self._next_state = self.ALIVE
        elif upLeftStatus and not upStatus and upRightStatus:
            self._next_state = self.DEAD
        elif upLeftStatus and not upStatus and not upRightStatus:
            self._next_state = self.ALIVE
        elif not upLeftStatus and upStatus and upRightStatus:
            self._next_state = self.ALIVE
        elif not upLeftStatus and upStatus and not upRightStatus:
            self._next_state = self.DEAD
        elif not upLeftStatus and not upStatus and upRightStatus:
            self._next_state = self.ALIVE
        elif not upLeftStatus and not upStatus and not upRightStatus:
            self._next_state = self.DEAD
      




    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state
