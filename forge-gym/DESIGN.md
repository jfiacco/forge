# Forge Gymnasium Environment - Design Document

## Overview

This document outlines the design for a Gymnasium-compatible environment that enables reinforcement learning agents to play Magic: The Gathering using the Forge game engine.

## Entry Point Analysis

### Command Line Entry
- **Main Class**: `forge-gui-desktop/src/main/java/forge/view/Main.java`
- **Command**: `sim` (simulation mode)
- **Implementation**: Calls `SimulateMatch.simulate(args)`

### Key Components

1. **Main.java** (Line 75-76)
   ```java
   case "sim":
       SimulateMatch.simulate(args);
       break;
   ```

2. **SimulateMatch.java** (Line 37-157)
   - Parses command-line arguments for deck selection, game count, format
   - Creates `Match` and `Game` objects
   - Runs game loop with AI players
   - Handles game outcomes and logging

3. **Game.java** (`forge-game/src/main/java/forge/game/Game.java`)
   - Core game state representation
   - Public methods for accessing state:
     * `getPlayers()` - Get all players
     * `getPhaseHandler()` - Current phase/turn info
     * `getStack()` - Stack state
     * `getCombat()` - Combat state
     * `isGameOver()` - Check if game ended
     * `getOutcome()` - Get game result

4. **GameSimulator.java** (`forge-ai/src/main/java/forge/ai/simulation/GameSimulator.java`)
   - AI decision making
   - `simulateSpellAbility()` - Evaluate actions
   - `getScoreForOrigGame()` - State evaluation
   - Uses `GameStateEvaluator` for scoring positions

## Architecture Considerations

### Why Real-Time Gymnasium (rtgym)?

The Forge game engine drives the simulation loop internally (Java-side), not the Python environment. This means:

1. **Asynchronous Game Loop**: The game progresses in Java at its own pace
2. **Event-Driven**: Python needs to react to game state changes
3. **Bidirectional Communication**: Python sends actions, Java sends state updates

rtgym (Real-Time Gymnasium) is designed exactly for this scenario where:
- The environment is not fully controlled by Python
- State updates happen asynchronously
- The Python side observes and influences but doesn't drive the loop

### Alternative Approaches

1. **Subprocess + JSON Protocol**
   - Launch Forge as subprocess
   - Communicate via stdin/stdout with JSON messages
   - Pros: Simple, language-agnostic
   - Cons: Overhead, serialization costs

2. **Py4J Bridge**
   - Direct Python-Java interop
   - Pros: Low latency, native object access
   - Cons: Complexity, platform-specific

3. **JNI/Jnius**
   - Call Java from Python directly
   - Pros: Fast, direct access
   - Cons: Complex setup, memory management

4. **REST API (WebSocket)**
   - Forge exposes HTTP/WS API
   - Pros: Language-agnostic, can run distributed
   - Cons: Network overhead, requires API implementation

**Recommendation**: Start with subprocess + JSON for simplicity, migrate to Py4J for performance if needed.

## Observation Space Design

Based on `Game.java` public methods:

```python
observation_space = spaces.Dict({
    # Player states
    'player_1_life': spaces.Box(low=-100, high=100, shape=(1,), dtype=np.int32),
    'player_2_life': spaces.Box(low=-100, high=100, shape=(1,), dtype=np.int32),
    'player_1_hand_size': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
    'player_2_hand_size': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
    
    # Battlefield state
    'player_1_creatures': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
    'player_2_creatures': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
    'player_1_lands': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
    'player_2_lands': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
    
    # Resources
    'player_1_mana': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
    'player_2_mana': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
    
    # Game metadata
    'current_phase': spaces.Discrete(8),  # PhaseType enum
    'turn_number': spaces.Box(low=0, high=1000, shape=(1,), dtype=np.int32),
    'stack_size': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
    'active_player': spaces.Discrete(2),  # Which player's turn
    
    # Optional: More detailed state
    # 'card_features': spaces.Box(...),  # Encoded card information
    # 'combat_state': spaces.MultiBinary(10),  # Is combat active, attackers, blockers
})
```

### State Extraction Methods

From `Game.java`:
- `game.getPlayers().get(0).getLife()` → life total
- `game.getPlayers().get(0).getCardsIn(ZoneType.Hand).size()` → hand size
- `game.getPlayers().get(0).getCardsIn(ZoneType.Battlefield).size()` → permanents
- `game.getPhaseHandler().getPhase()` → current phase
- `game.getPhaseHandler().getTurn()` → turn number
- `game.getStackZone().size()` → stack size
- `game.getPhaseHandler().getPlayerTurn()` → active player

## Action Space Design

Actions represent decisions the AI makes during the game:

```python
action_space = spaces.Discrete(N)  # where N is dynamic
```

### Action Mapping

- **Action 0**: Pass priority (do nothing)
- **Actions 1-N**: Index into available `SpellAbility` choices

The available actions change each decision point based on:
- Cards in hand
- Activated abilities on battlefield
- Game phase and priority

### Implementation Approach

1. **Query Available Actions**:
   ```java
   // From GameSimulator/SpellAbilityPicker
   List<SpellAbility> abilities = getAvailableAbilities(player);
   ```

2. **Encode Action List**:
   - Send list of available actions to Python
   - Each action has an index (0 = pass, 1-N = spell/ability)

3. **Decode Selected Action**:
   - Python returns action index
   - Java executes corresponding `SpellAbility`

### Action Masking

Since not all actions are valid at all times:
- Use Gymnasium's action masking feature
- Pass valid action mask with observation
- Prevents agent from selecting invalid actions

```python
info = {
    'action_mask': np.array([1, 1, 0, 1, ...])  # 1 = valid, 0 = invalid
}
```

## Reward Design

### Basic Rewards

- **Win**: +1.0
- **Loss**: -1.0
- **Draw**: 0.0

### Shaped Rewards (Optional)

For faster learning, can add intermediate rewards:

1. **Life Differential**:
   ```python
   reward = (my_life - opp_life) / 100.0
   ```

2. **Card Advantage**:
   ```python
   card_advantage = (my_cards - opp_cards) / 10.0
   ```

3. **Board State Value**:
   Use Forge's `GameStateEvaluator.Score`:
   ```java
   Score score = evaluator.getScoreForGameState(game, player);
   reward = score.value / normalizing_factor;
   ```

4. **Phase-based Rewards**:
   - Reward for successfully resolving spells
   - Penalty for passing when having playable cards
   - Reward for efficient mana usage

## Implementation Steps

### Phase 1: Basic Infrastructure
1. Create Python package structure ✓
2. Define Gymnasium environment skeleton ✓
3. Design observation/action spaces ✓
4. Document architecture ✓

### Phase 2: Java-Python Bridge
1. Modify `SimulateMatch.java` to accept control commands
2. Implement JSON protocol for state/action exchange
3. Create Python bridge module to launch/communicate with Java
4. Test basic communication

### Phase 3: State Extraction
1. Add methods to extract observation from `Game` object
2. Serialize game state to JSON/protobuf
3. Implement Python deserialization
4. Validate observation space matches design

### Phase 4: Action Integration
1. Implement action list querying
2. Add action selection mechanism
3. Connect Python action choices to `GameSimulator`
4. Test action execution

### Phase 5: Reward & Episode Management
1. Implement reward calculation
2. Handle episode termination (win/loss/draw)
3. Add episode reset functionality
4. Test full episode lifecycle

### Phase 6: rtgym Integration
1. Implement `ForgeRTGymInterface` class
2. Handle asynchronous state updates
3. Add proper threading/synchronization
4. Test with real-time game stepping

### Phase 7: Polish & Optimization
1. Add logging and debugging tools
2. Optimize communication overhead
3. Add configuration options (decks, formats, etc.)
4. Write comprehensive tests
5. Create example agents and tutorials

## Usage Examples

### Basic Random Agent
```python
import gymnasium as gym
import forge_gym

env = gym.make('ForgeAI-v0')
obs, info = env.reset()

for _ in range(1000):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break
```

### With Action Masking
```python
obs, info = env.reset()
action_mask = info['action_mask']

# Only sample from valid actions
valid_actions = np.where(action_mask == 1)[0]
action = np.random.choice(valid_actions)
```

### Training with Stable-Baselines3
```python
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

env = DummyVecEnv([lambda: gym.make('ForgeAI-v0')])
model = PPO('MultiInputPolicy', env, verbose=1)
model.learn(total_timesteps=100000)
```

### Using rtgym
```python
from rtgym import RealTimeGymInterface
from forge_gym.envs.forge_env import ForgeRTGymInterface

interface = ForgeRTGymInterface(
    forge_path='path/to/forge.jar',
    deck1='deck1.dck',
    deck2='deck2.dck'
)

env = gym.make('ForgeAI-v0', interface=interface)
# Use normally with rtgym handling the async stepping
```

## Testing Strategy

1. **Unit Tests**:
   - Test state extraction
   - Test action encoding/decoding
   - Test reward calculation

2. **Integration Tests**:
   - Test full episode with random actions
   - Test communication bridge
   - Test episode reset

3. **System Tests**:
   - Run full games with trained agents
   - Validate against Forge's native AI
   - Performance benchmarks

## Performance Considerations

- **Latency**: Java-Python bridge adds overhead (~1-10ms per call)
- **Throughput**: Target 10-100 steps/second
- **Memory**: Each game state ~1-10MB depending on complexity
- **Parallelization**: Can run multiple games in parallel for training

## Future Enhancements

1. **Visual Observations**: Use card images/board rendering
2. **Advanced Features**: Deck building, mulligans, sideboarding
3. **Multi-Agent**: Support for multiplayer formats
4. **Distributed Training**: Run many games across multiple machines
5. **Curriculum Learning**: Start with simple decks/formats, progress to complex
6. **Imitation Learning**: Learn from recorded games
7. **Self-Play**: Train agents by playing against themselves

## References

- Forge Repository: https://github.com/jfiacco/forge
- Gymnasium: https://gymnasium.farama.org/
- rtgym: https://github.com/yannbouteiller/rtgym
- Stable-Baselines3: https://stable-baselines3.readthedocs.io/
