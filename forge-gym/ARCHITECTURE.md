# Forge Gymnasium Environment - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Python Side (RL Agent)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐         ┌────────────────────────────────┐   │
│  │  RL Framework    │────────▶│   ForgeEnv (Gymnasium)         │   │
│  │  (SB3, RLlib,    │         │   - reset()                     │   │
│  │   custom, etc.)  │◀────────│   - step(action)               │   │
│  └──────────────────┘         │   - render()                    │   │
│                                │   - close()                     │   │
│                                └───────────┬────────────────────┘   │
│                                            │                          │
│                                            │ Communication Bridge     │
│                                            │ (JSON/IPC/Py4J)          │
└────────────────────────────────────────────┼─────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Java Side (Forge Engine)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Main.java (Entry Point)                                      │   │
│  │   - main(args) with "sim" mode                              │   │
│  └────────────────────────┬─────────────────────────────────────┘   │
│                            │                                          │
│                            ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ SimulateMatch.java                                           │   │
│  │   - simulate(args)                                           │   │
│  │   - Parse decks, rules                                       │   │
│  │   - Create Match and Game                                    │   │
│  └────────────────────────┬─────────────────────────────────────┘   │
│                            │                                          │
│                            ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Match.java                                                   │   │
│  │   - createGame()                                             │   │
│  │   - startGame(game)                                          │   │
│  │   - Manages series of games                                  │   │
│  └────────────────────────┬─────────────────────────────────────┘   │
│                            │                                          │
│           ┌────────────────┴────────────────┐                        │
│           │                                  │                        │
│           ▼                                  ▼                        │
│  ┌────────────────┐              ┌─────────────────────────┐        │
│  │ Game.java      │              │ GameSimulator.java      │        │
│  │ (State)        │◀────────────▶│ (AI Logic)              │        │
│  │                │              │                         │        │
│  │ - getPlayers() │              │ - simulateSpellAbility()│        │
│  │ - getPhase()   │              │ - getScoreForOrigGame() │        │
│  │ - getStack()   │              │                         │        │
│  │ - getCombat()  │              │  Uses:                  │        │
│  │ - isGameOver() │              │  ┌──────────────────┐  │        │
│  └────────────────┘              │  │GameStateEvaluator│  │        │
│                                   │  └──────────────────┘  │        │
│                                   └─────────────────────────┘        │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Communication Flow

### 1. Episode Start (reset)

```
Python                          Java
  │                              │
  │──── reset() ───────────────▶ │
  │                              │
  │                              │ Launch sim mode
  │                              │ Initialize decks
  │                              │ Create Game
  │                              │
  │◀─── initial_state ────────── │
  │                              │
  │ Return observation, info     │
```

### 2. Action Step

```
Python                          Java
  │                              │
  │──── step(action) ─────────▶ │
  │                              │
  │                              │ Map action to SpellAbility
  │                              │ Execute in GameSimulator
  │                              │ Update Game state
  │                              │ Check if game over
  │                              │
  │◀─── new_state, reward ────── │
  │                              │
  │ Return obs, reward, done     │
```

### 3. Game Loop (Real-Time via rtgym)

```
Python (rtgym wrapper)          Java (Game Loop)
  │                              │
  │                              │ Game runs continuously
  │                              │    │
  │◀──── state_update ──────────────┤
  │                              │    │
  │ Process observation          │    │
  │ Agent decides action         │    │
  │                              │    │
  │──── action ─────────────────────▶│
  │                              │    │
  │                              │ Execute action
  │                              │ Continue game loop
  │                              │    │
  │◀──── state_update ──────────────┤
  │                              │    │
  └──────────────────────────────    └────▶
```

## Data Structures

### Observation (Python → from Java)

```python
observation = {
    # Player state
    'player_1_life': np.array([20], dtype=np.int32),
    'player_2_life': np.array([20], dtype=np.int32),
    'player_1_hand_size': np.array([7], dtype=np.int32),
    'player_2_hand_size': np.array([7], dtype=np.int32),
    
    # Board state
    'player_1_creatures': np.array([0], dtype=np.int32),
    'player_2_creatures': np.array([0], dtype=np.int32),
    'player_1_mana': np.array([0], dtype=np.int32),
    'player_2_mana': np.array([0], dtype=np.int32),
    
    # Game metadata
    'current_phase': 0,  # 0-7 for different phases
    'turn_number': np.array([1], dtype=np.int32),
    'stack_size': np.array([0], dtype=np.int32),
}
```

### Action (Python → Java)

```python
action = 42  # Index into available actions

# Internally maps to:
# 0 = pass priority
# 1-N = specific SpellAbility from Game.getPlayers().get(0).getAvailableActions()
```

### State Message (Java → Python via JSON)

```json
{
  "game_id": 12345,
  "turn": 5,
  "phase": "MAIN_1",
  "active_player": 0,
  "players": [
    {
      "id": 0,
      "life": 18,
      "hand_size": 5,
      "creatures": 2,
      "lands": 4,
      "mana_available": {"W": 2, "U": 1, "B": 0, "R": 0, "G": 1}
    },
    {
      "id": 1,
      "life": 20,
      "hand_size": 6,
      "creatures": 1,
      "lands": 3,
      "mana_available": {"W": 0, "U": 2, "B": 1, "R": 0, "G": 0}
    }
  ],
  "stack": [],
  "available_actions": [
    {"id": 0, "type": "pass"},
    {"id": 1, "type": "cast_spell", "card": "Lightning Bolt"},
    {"id": 2, "type": "activate_ability", "source": "Llanowar Elves"}
  ],
  "game_over": false,
  "winner": null
}
```

### Action Message (Python → Java via JSON)

```json
{
  "action_id": 1,
  "targets": [12, 34],  // Optional: target IDs if required
  "choices": ["choice1"] // Optional: for modal spells
}
```

## Key Classes and Methods

### Python Side

#### ForgeEnv (forge_gym/envs/forge_env.py)
- `__init__(render_mode)`: Initialize environment
- `reset(seed, options)`: Start new game, return initial observation
- `step(action)`: Execute action, return observation, reward, done, info
- `_get_observation()`: Extract state from Java Game object
- `_calculate_reward()`: Compute reward based on game outcome
- `_is_game_over()`: Check if episode should terminate
- `render()`: Display game state
- `close()`: Clean up resources

#### ForgeRTGymInterface (forge_gym/envs/forge_env.py)
- For integration with rtgym when implemented
- Handles asynchronous game loop interaction

### Java Side

#### Main.java (forge-gui-desktop/src/main/java/forge/view/Main.java)
- **Entry Point**: `main(String[] args)`
- **Sim Mode**: `case "sim": SimulateMatch.simulate(args)`

#### SimulateMatch.java (forge-gui-desktop/src/main/java/forge/view/SimulateMatch.java)
- `simulate(String[] args)`: Main simulation entry point
- Parse command-line arguments for deck, format, game count
- Create Match and RegisteredPlayer objects
- Run game loop

#### Game.java (forge-game/src/main/java/forge/game/Game.java)
- **State Access**:
  - `getPlayers()`: PlayerCollection
  - `getPhaseHandler()`: PhaseHandler (for turn/phase info)
  - `getStack()`: MagicStack (for stack state)
  - `getCombat()`: Combat (for combat state)
  - `isGameOver()`: boolean
  - `getOutcome()`: GameOutcome (winner, reason)

#### GameSimulator.java (forge-ai/src/main/java/forge/ai/simulation/GameSimulator.java)
- `simulateSpellAbility(SpellAbility)`: Evaluate action
- `getScoreForOrigGame()`: Get state evaluation
- Works with GameStateEvaluator for position scoring

#### GameStateEvaluator.java (forge-ai/src/main/java/forge/ai/simulation/GameStateEvaluator.java)
- `getScoreForGameState(Game, Player)`: Evaluate position
- Returns Score object with numeric value
- Can be used for shaped rewards

## Implementation Phases

### Phase 1: Skeleton ✓
- [x] Create Python package structure
- [x] Define Gymnasium environment interface
- [x] Design observation/action spaces
- [x] Document architecture

### Phase 2: Java Bridge (TODO)
- [ ] Modify SimulateMatch to accept control commands
- [ ] Implement JSON/IPC protocol
- [ ] Create Python subprocess launcher
- [ ] Test bidirectional communication

### Phase 3: State Integration (TODO)
- [ ] Extract observations from Game object
- [ ] Serialize to JSON
- [ ] Deserialize in Python
- [ ] Validate observation space

### Phase 4: Action Integration (TODO)
- [ ] Query available actions from GameSimulator
- [ ] Send action selection from Python
- [ ] Execute in Java
- [ ] Return new state

### Phase 5: Rewards & Episodes (TODO)
- [ ] Implement reward calculation
- [ ] Handle game termination
- [ ] Episode reset functionality
- [ ] Test complete episode lifecycle

### Phase 6: rtgym (TODO)
- [ ] Implement ForgeRTGymInterface
- [ ] Handle async state updates
- [ ] Threading/synchronization
- [ ] Test real-time stepping

### Phase 7: Polish (TODO)
- [ ] Logging and debugging
- [ ] Configuration options
- [ ] Documentation
- [ ] Example agents
- [ ] Tests

## Integration Approaches

### Option 1: Subprocess + JSON (Recommended for Start)

**Pros:**
- Simple to implement
- Language-agnostic
- Easy debugging
- Clean separation

**Cons:**
- Serialization overhead
- IPC latency (~1-5ms per message)

**Implementation:**
```python
import subprocess
import json

# Python side
process = subprocess.Popen(
    ['java', '-jar', 'forge.jar', 'sim', '--agent-mode'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send action
action_msg = json.dumps({'action': 42})
process.stdin.write(action_msg + '\n')
process.stdin.flush()

# Receive state
state_msg = process.stdout.readline()
state = json.loads(state_msg)
```

### Option 2: Py4J (For Production)

**Pros:**
- Direct Java object access
- Low latency
- Rich type support

**Cons:**
- More complex setup
- Platform dependencies
- Memory management

**Implementation:**
```python
from py4j.java_gateway import JavaGateway

gateway = JavaGateway()
game = gateway.entry_point.createGame(deck1, deck2)
life = game.getPlayers().get(0).getLife()
```

### Option 3: JNI/Jnius

**Pros:**
- Native performance
- Direct integration

**Cons:**
- Most complex
- Platform-specific builds
- Memory management challenges

## Testing Strategy

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test Python-Java communication
3. **System Tests**: Test full game episodes
4. **Performance Tests**: Measure throughput and latency
5. **Validation Tests**: Compare against Forge's native AI

## Performance Targets

- **Latency**: < 10ms per step
- **Throughput**: > 100 steps/second
- **Memory**: < 100MB per environment
- **Parallelization**: Support 10+ parallel envs

## Next Steps

1. Implement subprocess bridge in Python
2. Modify SimulateMatch.java to accept JSON commands
3. Test basic communication
4. Implement state extraction
5. Implement action execution
6. Test full episode
