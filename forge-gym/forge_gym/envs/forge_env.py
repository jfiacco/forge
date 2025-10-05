"""
Gymnasium environment for Forge Magic: The Gathering AI.

This environment provides a Gymnasium-compatible interface to the Forge game simulator.
Since the game is driven by the Java simulator (not Python), this implementation is
designed to work with Real-Time Gymnasium (rtgym) for asynchronous game stepping.

Entry Point: forge-gui-desktop/src/main/java/forge/view/Main.java
Command: 'sim' mode invokes SimulateMatch.simulate()
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Any, Dict, Optional, Tuple


class ForgeEnv(gym.Env):
    """
    Gymnasium environment for training RL agents to play Magic: The Gathering via Forge.
    
    This is a skeleton implementation that outlines the structure needed to interface
    with Forge's simulation mode. A complete implementation would require:
    1. Java-Python bridge (py4j, jnius, or subprocess with IPC)
    2. Game state extraction from forge.game.Game
    3. Action encoding/decoding for SpellAbility choices
    4. Integration with rtgym for real-time stepping
    
    Observation Space:
        - Player 1 life total (int)
        - Player 2 life total (int)
        - Player 1 cards in hand (int)
        - Player 2 cards in hand (int)
        - Player 1 creatures on battlefield (int)
        - Player 2 creatures on battlefield (int)
        - Player 1 total mana available (int)
        - Player 2 total mana available (int)
        - Current phase (categorical, 0-7)
        - Current turn number (int)
        - Stack size (int)
        - Additional state features can be added based on Game.java public methods:
          * getMonarch(), getPhaseHandler(), getCombat(), etc.
    
    Action Space:
        Actions represent AI decisions:
        - Discrete space of possible spell/ability activations
        - 0: Pass priority (no action)
        - 1-N: Cast spell/activate ability at index i
        
        In a full implementation, this would map to:
        - SpellAbility choices from GameSimulator
        - Target selections
        - Combat decisions
    
    Reward:
        - +1 for winning the game
        - -1 for losing the game
        - 0 for ongoing game
        - Can be extended with shaped rewards based on:
          * Life total differential
          * Card advantage
          * Board state evaluation (from GameStateEvaluator)
    """
    
    metadata = {
        'render_modes': ['human', 'ansi'],
        'render_fps': 1,
    }
    
    def __init__(self, render_mode: Optional[str] = None):
        """
        Initialize the Forge environment.
        
        Args:
            render_mode: How to render the environment ('human' for GUI, 'ansi' for text)
        """
        super().__init__()
        
        self.render_mode = render_mode
        
        # Define observation space
        # This is a simplified version - expand based on needs
        self.observation_space = spaces.Dict({
            'player_1_life': spaces.Box(low=-100, high=100, shape=(1,), dtype=np.int32),
            'player_2_life': spaces.Box(low=-100, high=100, shape=(1,), dtype=np.int32),
            'player_1_hand_size': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
            'player_2_hand_size': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
            'player_1_creatures': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
            'player_2_creatures': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
            'player_1_mana': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
            'player_2_mana': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
            'current_phase': spaces.Discrete(8),  # Untap, Upkeep, Draw, Main1, Combat, Main2, End, Cleanup
            'turn_number': spaces.Box(low=0, high=1000, shape=(1,), dtype=np.int32),
            'stack_size': spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
        })
        
        # Define action space
        # In a real implementation, this would be dynamic based on available actions
        # For now, use a fixed discrete space
        self.action_space = spaces.Discrete(1000)  # 0 = pass, 1-999 = possible actions
        
        # State tracking
        self.game_process = None
        self.current_state = None
        self.episode_step = 0
        
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """
        Reset the environment to start a new game.
        
        Args:
            seed: Random seed for reproducibility
            options: Additional options (e.g., deck choices)
        
        Returns:
            observation: Initial game state
            info: Additional information
        """
        super().reset(seed=seed)
        
        self.episode_step = 0
        
        # TODO: Start a new Forge simulation
        # This would involve:
        # 1. Launching the Java process with 'sim' command
        # 2. Setting up decks (from options or defaults)
        # 3. Initializing the game
        # 4. Extracting initial game state
        
        # For now, return a dummy observation
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def step(
        self, action: int
    ) -> Tuple[Dict[str, np.ndarray], float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.
        
        Args:
            action: The action to take (spell/ability index or pass)
        
        Returns:
            observation: New game state after the action
            reward: Reward for this step
            terminated: Whether the game is over (win/loss)
            truncated: Whether the episode should end (timeout, error)
            info: Additional information
        """
        self.episode_step += 1
        
        # TODO: Send action to Forge simulator
        # This would involve:
        # 1. Translating action index to SpellAbility selection
        # 2. Sending to GameSimulator through the bridge
        # 3. Waiting for game state update
        # 4. Extracting new observation
        
        # Get updated observation
        observation = self._get_observation()
        
        # Calculate reward
        reward = self._calculate_reward()
        
        # Check if game is over
        terminated = self._is_game_over()
        truncated = self.episode_step >= 10000  # Max episode length
        
        # Get additional info
        info = self._get_info()
        
        return observation, reward, terminated, truncated, info
    
    def render(self):
        """
        Render the current game state.
        
        For 'human' mode, this could display the GUI or a visual representation.
        For 'ansi' mode, print text representation to console.
        """
        if self.render_mode == 'ansi':
            # Print game state to console
            if self.current_state:
                print(f"Turn: {self.current_state.get('turn_number', [0])[0]}")
                print(f"Player 1 Life: {self.current_state.get('player_1_life', [0])[0]}")
                print(f"Player 2 Life: {self.current_state.get('player_2_life', [0])[0]}")
                print(f"Phase: {self.current_state.get('current_phase', 0)}")
        elif self.render_mode == 'human':
            # In a full implementation, this might trigger Forge's GUI
            pass
    
    def close(self):
        """Clean up resources, terminate Java process if running."""
        if self.game_process is not None:
            # TODO: Gracefully terminate the Forge simulator
            self.game_process = None
    
    def _get_observation(self) -> Dict[str, np.ndarray]:
        """
        Extract the current game state as an observation.
        
        In a full implementation, this would:
        1. Query the Game object via the bridge
        2. Call methods like:
           - game.getPlayers().get(0).getLife()
           - game.getPlayers().get(0).getCardsIn(ZoneType.Hand).size()
           - game.getPhaseHandler().getPhase()
           - game.getStackZone().size()
        3. Package into the observation space format
        
        Returns:
            Dictionary observation matching observation_space
        """
        # Dummy observation for skeleton
        self.current_state = {
            'player_1_life': np.array([20], dtype=np.int32),
            'player_2_life': np.array([20], dtype=np.int32),
            'player_1_hand_size': np.array([7], dtype=np.int32),
            'player_2_hand_size': np.array([7], dtype=np.int32),
            'player_1_creatures': np.array([0], dtype=np.int32),
            'player_2_creatures': np.array([0], dtype=np.int32),
            'player_1_mana': np.array([0], dtype=np.int32),
            'player_2_mana': np.array([0], dtype=np.int32),
            'current_phase': 0,  # Untap
            'turn_number': np.array([1], dtype=np.int32),
            'stack_size': np.array([0], dtype=np.int32),
        }
        return self.current_state
    
    def _calculate_reward(self) -> float:
        """
        Calculate the reward for the current state.
        
        Basic reward structure:
        - Game won: +1
        - Game lost: -1
        - Ongoing: 0 (or shaped reward)
        
        Could be enhanced with shaped rewards:
        - Life differential: (my_life - opp_life) / 100.0
        - Card advantage
        - GameStateEvaluator.Score from Forge
        
        Returns:
            Reward value
        """
        # TODO: Check game outcome from Game.getOutcome()
        return 0.0
    
    def _is_game_over(self) -> bool:
        """
        Check if the game has ended.
        
        In a full implementation, check:
        - game.isGameOver()
        - game.getOutcome().isDraw()
        - game.getOutcome().getWinningLobbyPlayer()
        
        Returns:
            True if game is over, False otherwise
        """
        # TODO: Check game state
        return False
    
    def _get_info(self) -> Dict[str, Any]:
        """
        Get additional information about the current state.
        
        Returns:
            Dictionary with supplementary information
        """
        return {
            'episode_step': self.episode_step,
            # Could include:
            # 'game_id': game.getId(),
            # 'winner': game.getOutcome().getWinningLobbyPlayer() if game over,
            # 'reason': game.getOutcome().getWinReasonString(),
        }


# For use with rtgym (Real-Time Gymnasium)
# This would be the recommended approach for integration
class ForgeRTGymInterface:
    """
    Interface class for using Forge with Real-Time Gymnasium (rtgym).
    
    rtgym is needed because Forge's game loop runs in Java and drives the simulation,
    rather than being driven by the Python environment's step() calls.
    
    This class would implement the rtgym interface methods:
    - get_obs_rew_terminated_info(): Called by rtgym to get current state
    - wait_for_obs_rew_terminated_info(): Wait for state updates
    - send_control(action): Send action to the game
    - reset(): Reset the game
    
    See: https://github.com/yannbouteiller/rtgym
    """
    
    def __init__(self, forge_path: str, deck1: str, deck2: str):
        """
        Initialize the rtgym interface.
        
        Args:
            forge_path: Path to Forge executable/JAR
            deck1: Path to first deck file
            deck2: Path to second deck file
        """
        self.forge_path = forge_path
        self.deck1 = deck1
        self.deck2 = deck2
        self.game_process = None
        
    def get_observation_space(self):
        """Return the observation space for rtgym."""
        # Same as ForgeEnv.observation_space
        pass
    
    def get_action_space(self):
        """Return the action space for rtgym."""
        # Same as ForgeEnv.action_space
        pass
    
    def reset(self):
        """Reset the game by starting a new Forge simulation."""
        # Start Forge with: java -jar forge.jar sim -d deck1 -d deck2
        pass
    
    def get_obs_rew_terminated_info(self):
        """Get current observation, reward, termination status, and info."""
        # Extract from game state
        pass
    
    def send_control(self, action):
        """Send an action (control) to the game."""
        # Send action to GameSimulator
        pass
