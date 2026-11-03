import random

class AdvancedVacuumAgent:
    def __init__(self, start_location='A'):
        self.location = start_location

    def perceive(self, environment):
        """Perceives the state of the current room."""
        return environment[self.location]

    def act(self, environment):
        """
        Perceive-and-act method incorporating the bonus logic:
        - If current room is dirty, clean it.
        - If current room is clean, look for other dirty rooms and randomly 
          jump to one, or just move normally if all are clean.
        """
        status = self.perceive(environment)
        
        if status == 'Dirty':
            self.clean(environment)
            return 'Cleaned current room'
        else:
            # Bonus Task logic: find all dirty rooms
            dirty_rooms = [room for room, state in environment.items() if state == 'Dirty']
            
            if dirty_rooms:
                # Randomly choose which dirty room to visit next
                self.location = random.choice(dirty_rooms)
                return f'Moved randomly to dirty Room {self.location}'
            else:
                # If all rooms are clean, cycle to another room
                rooms = list(environment.keys())
                current_idx = rooms.index(self.location)
                self.location = rooms[(current_idx + 1) % len(rooms)]
                return f'All rooms clean. Cycled to Room {self.location}'

    def clean(self, environment):
        """Cleans the current room."""
        environment[self.location] = 'Clean'


def display_grid(environment, agent_location):
    """
    Bonus Task: Visualize the agent moving between rooms using a text-based grid.
    """
    print("|   Environment     |")
    for room, state in environment.items():
        agent_here = " <-- [AGENT]" if room == agent_location else ""
        print(f"| Room {room}: {state:<6} {agent_here:<12} |")

def run_simulation():
    print("--- Environment Setup (Including Bonus Room C) ---")
    environment = {
        'A': input("Enter initial state for Room A (Dirty/Clean): ").capitalize(),
        'B': input("Enter initial state for Room B (Dirty/Clean): ").capitalize(),
        'C': input("Enter initial state for Room C (Dirty/Clean): ").capitalize()
    }
    
    start_loc = input("Enter agent's starting room (A, B, or C): ").upper()
    if start_loc not in environment:
        start_loc = 'A'
        
    agent = AdvancedVacuumAgent(start_location=start_loc)
    
    try:
        steps = int(input("Enter the number of simulation steps to run: "))
    except ValueError:
        steps = 5

    print("\n--- Simulation Started ---")
    for step in range(1, steps + 1):
        print(f"\nSTEP {step}")
        
        # Display visual grid before action
        display_grid(environment, agent.location)
        
        # Agent perceives and acts
        action = agent.act(environment)
        print(f"\n-> Action Taken: {action}")
        
        # Display environment state after action
        display_grid(environment, agent.location)

if __name__ == "__main__":
    run_simulation()