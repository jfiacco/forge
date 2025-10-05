# Quick Start Guide

## Installation

```bash
cd forge-gym
pip install -e .
```

## Basic Usage

### Simple Random Agent

```python
import gymnasium as gym
import forge_gym

# Create the environment
env = gym.make('ForgeAI-v0')

# Run a simple episode
obs, info = env.reset()
total_reward = 0

for step in range(100):
    # Sample a random action
    action = env.action_space.sample()
    
    # Take a step
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward
    
    if terminated or truncated:
        print(f"Episode finished after {step+1} steps")
        print(f"Total reward: {total_reward}")
        break

env.close()
```

### With Rendering

```python
import gymnasium as gym
import forge_gym

env = gym.make('ForgeAI-v0', render_mode='ansi')

obs, info = env.reset()
for _ in range(10):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    
    # Display the current state
    env.render()
    
    if terminated or truncated:
        break

env.close()
```

### Inspecting the Environment

```python
import gymnasium as gym
import forge_gym

env = gym.make('ForgeAI-v0')

print("Observation Space:", env.observation_space)
print("Action Space:", env.action_space)

obs, info = env.reset()
print("\nInitial Observation:")
for key, value in obs.items():
    print(f"  {key}: {value}")

env.close()
```

## Running Tests

```bash
cd forge-gym
pip install pytest
pytest tests/test_env.py -v
```

Expected output:
```
11 passed, 1 warning
```

## Running Examples

```bash
cd forge-gym
python examples/basic_usage.py
```

## What Works Now

✅ Environment creation and registration
✅ Observation space with game state
✅ Action space for decisions
✅ Reset functionality
✅ Step functionality (skeleton)
✅ Rendering (text mode)
✅ All tests passing

## What Needs Implementation

The skeleton is complete, but actual gameplay requires:

1. **Java-Python Bridge**: Communication layer between Python and Forge
2. **State Extraction**: Pull real game state from Game.java
3. **Action Execution**: Send actions to GameSimulator.java
4. **Rewards**: Calculate from actual game outcomes

See DESIGN.md and ARCHITECTURE.md for implementation details.

## Entry Point Reference

The Forge simulation mode is accessed via:
- **Command**: `forge.exe sim -d deck1.dck -d deck2.dck`
- **Java Entry**: `forge-gui-desktop/src/main/java/forge/view/Main.java` (line 75-76)
- **Implementation**: `SimulateMatch.simulate(args)`

## Training with RL Libraries

Once the Java bridge is implemented:

### Stable-Baselines3
```python
from stable_baselines3 import PPO
import forge_gym

env = gym.make('ForgeAI-v0')
model = PPO('MultiInputPolicy', env, verbose=1)
model.learn(total_timesteps=100000)
model.save('forge_agent')
```

### Custom Training Loop
```python
import torch
import torch.nn as nn
from torch.distributions import Categorical

# Your custom agent here
agent = YourAgent()

for episode in range(1000):
    obs, info = env.reset()
    done = False
    
    while not done:
        action = agent.select_action(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        
        agent.update(reward)
```

## Observation Space Details

The observation is a dictionary with:
- `player_1_life`: Life total (20 at start)
- `player_2_life`: Life total (20 at start)
- `player_1_hand_size`: Cards in hand
- `player_2_hand_size`: Cards in hand
- `player_1_creatures`: Creatures on battlefield
- `player_2_creatures`: Creatures on battlefield
- `player_1_mana`: Available mana
- `player_2_mana`: Available mana
- `current_phase`: Game phase (0-7)
- `turn_number`: Current turn
- `stack_size`: Number of spells on stack

## Action Space Details

Discrete space with 1000 possible actions:
- Action 0: Pass priority (do nothing)
- Actions 1-999: Cast spell or activate ability

In actual implementation, available actions will be dynamic based on game state.

## Need Help?

- See `README.md` for overview
- See `DESIGN.md` for detailed design
- See `ARCHITECTURE.md` for system architecture
- See `SUMMARY.md` for implementation status
- Check `tests/test_env.py` for examples
- Run `examples/basic_usage.py` for demo

## Next Steps

To complete the implementation:

1. **Set up Java Development Environment**
   - Build Forge from source
   - Understand Maven/Gradle build

2. **Create Communication Protocol**
   - Design JSON message format
   - Implement subprocess launcher in Python
   - Modify SimulateMatch.java to accept commands

3. **Implement State Extraction**
   - Add methods to serialize Game state
   - Test observation extraction

4. **Implement Action Execution**
   - Map Python actions to SpellAbility
   - Test action execution

5. **Train Your First Agent**
   - Use simple deck with basic cards
   - Train with PPO or similar
   - Evaluate against Forge AI

Good luck! 🎮🤖
