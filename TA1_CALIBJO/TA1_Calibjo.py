import agentpy as ap
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# STEP 1: GET USER INPUT FROM CONSOLE
print("--- Modified Random Walk Simulation Setup ---")
num_agents = int(input("Enter number of agents: "))
grid_size = int(input("Enter grid size (e.g., 10 for 10x10): "))
num_steps = int(input("Enter number of steps: "))



# STEP 2: MODIFIED AGENT DEFINITION (Tasks 1 & 2)
class ModifiedWalker(ap.Agent):
    """Defines agent behavior with path tracking and modified movement rules."""

    def step(self):
        """
        Executes a modified step: 
        Task 2 Modification: Introduces a preferred directional bias (higher chance 
        to move Up and Right) alongside standard random movement.
        """
        # Weighted choices to create a preferred movement bias towards top-right
        # (1,0)=Right, (0,1)=Up appear more frequently in the choice pool
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (0, 1), (1, 0)]
        direction = random.choice(directions)
        
        # Get current coordinates
        x, y = self.position
        
        # Keep agents inside grid boundaries (clamping)
        x = max(0, min(self.model.p.grid_size[0] - 1, x + direction[0]))
        y = max(0, min(self.model.p.grid_size[1] - 1, y + direction[1]))
        
        # Update current position
        self.position = (x, y)
        
        # Task 1 Requirement: Record current position into the agent's path history
        self.path.append(self.position)


# STEP 3: MODEL DEFINITION
class ModifiedRandomWalkModel(ap.Model):
    """Manages the simulation environment, grid, and modified agents."""
    
    def setup(self):
        """Initializes agents, random starting points, paths, and grid."""
        self.agents = ap.AgentList(self, self.p.agents, ModifiedWalker)
        
        for agent in self.agents:
            agent.position = (
                random.randint(0, self.p.grid_size[0] - 1),
                random.randint(0, self.p.grid_size[1] - 1)
            )
            # Initialize path history with starting position
            agent.path = [agent.position]
            
        # Create non-torus (bounded) grid
        self.grid = ap.Grid(self, self.p.grid_size, torus=False)
        self.grid.add_agents(self.agents)

    def step(self):
        """Advances the simulation model by one step."""
        self.agents.step()



# STEP 4: PARAMETERS & MODEL INITIALIZATION
parameters = {
    'agents': num_agents,
    'grid_size': (grid_size, grid_size),
    'steps': num_steps
}

model = ModifiedRandomWalkModel(parameters)
model.setup()


# ==========================================
# STEP 5: VISUALIZATION WITH TRAILING PATHS
# ==========================================
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-0.5, model.p.grid_size[0] - 0.5)
ax.set_ylim(-0.5, model.p.grid_size[1] - 0.5)
ax.set_xticks(range(model.p.grid_size[0]))
ax.set_yticks(range(model.p.grid_size[1]))
ax.grid(True)
ax.set_title(f"Modified Random Walk ({num_agents} Agents, {grid_size}x{grid_size} Grid)")

# Create plot line handles for each agent to display their tracked paths (Task 1)
lines = [ax.plot([], [], marker='o', linestyle='-', linewidth=1.5, label=f'Agent {i+1}')[0] 
         for i in range(model.p.agents)]

def update(frame):
    """Animation update function showing real-time path trajectories."""
    model.step()
    
    # Update each agent's path line data
    for i, agent in enumerate(model.agents):
        x_coords = [p[0] for p in agent.path]
        y_coords = [p[1] for p in agent.path]
        lines[i].set_data(x_coords, y_coords)
        
    return lines

ani = animation.FuncAnimation(
    fig, update, frames=model.p.steps, interval=300, blit=False, repeat=False
)

plt.legend(loc='upper right', fontsize='small')
plt.show()



# STEP 6: FINAL POSITION ANALYSIS (Task 3)
print("\n--- Final Position Analysis ---")
for i, agent in enumerate(model.agents):
    print(f"Agent {i+1} Final Position: {agent.position} | Total Steps Taken: {len(agent.path) - 1}")