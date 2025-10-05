# Forge Gymnasium Environment

A Python Gymnasium (formerly OpenAI Gym) environment for training reinforcement learning agents to play Magic: The Gathering using the Forge game engine.

## Overview

This module provides a Gymnasium-compatible interface to the Forge AI simulation mode. Since Forge's game loop is driven by the Java simulator rather than the Python side, this environment uses the Real-Time Gymnasium (rtgym) wrapper to bridge the two systems.

## Entry Point

The environment interfaces with Forge's command-line simulation mode:
- **Entry Point**: `forge-gui-desktop/src/main/java/forge/view/Main.java`
- **Command**: `sim` (launches `SimulateMatch.simulate()`)
- **Game State**: Accessed via `forge-game/src/main/java/forge/game/Game.java`
- **AI Logic**: `forge-ai/src/main/java/forge/ai/simulation/GameSimulator.java`

## Architecture

The environment follows a real-time approach using rtgym because:
1. The game simulation is driven by the Java-based Forge engine
2. The Python side acts as an observer/controller rather than the main loop driver
3. Game state updates happen asynchronously based on the simulator's pace

## Installation

```bash
cd forge-gym
pip install -e .
```

Dependencies:
- gymnasium
- numpy
- rtgym (for real-time environment wrapping)

## Usage

```python
import gymnasium as gym
import forge_gym

# Create the environment
env = gym.make('ForgeAI-v0')

# Standard Gymnasium interface
observation, info = env.reset()
done = False

while not done:
    # Your agent decides an action
    action = env.action_space.sample()  # Or use your trained agent
    
    # Step the environment
    observation, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated

env.close()
```

## Observation Space

The observation space includes key game state information:
- Player life totals
- Number of cards in hand
- Mana available
- Battlefield state (creatures, permanents)
- Stack state
- Phase/turn information

## Action Space

Actions correspond to decisions the AI needs to make:
- Which spell/ability to cast or activate
- Target selection for spells
- Combat decisions
- Pass priority

## Implementation Notes

Since this is a sketch/design document, the actual implementation would require:
1. A Java-Python bridge (e.g., py4j, jnius, or subprocess with JSON protocol)
2. Game state serialization/deserialization
3. Action encoding/decoding
4. Integration with rtgym for real-time stepping

## Contributing

This is a work in progress. Contributions are welcome to help bridge the Java game engine with Python RL frameworks.

## License

GPL-3.0 (same as Forge)
