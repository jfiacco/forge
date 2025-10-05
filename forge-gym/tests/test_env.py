"""
Tests for the Forge Gymnasium environment.

These tests validate the skeleton implementation. Once the Java bridge is
implemented, additional tests should be added for:
- State extraction
- Action execution
- Reward calculation
- Episode lifecycle
"""

import pytest
import gymnasium as gym
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import forge_gym


class TestForgeEnvBasics:
    """Test basic environment functionality."""
    
    def test_environment_registration(self):
        """Test that the environment is properly registered with Gymnasium."""
        env = gym.make('ForgeAI-v0')
        assert env is not None
        env.close()
    
    def test_observation_space(self):
        """Test that observation space is properly defined."""
        env = gym.make('ForgeAI-v0')
        
        # Check that observation space is a Dict
        assert isinstance(env.observation_space, gym.spaces.Dict)
        
        # Check for required keys
        required_keys = {
            'player_1_life', 'player_2_life',
            'player_1_hand_size', 'player_2_hand_size',
            'player_1_creatures', 'player_2_creatures',
            'player_1_mana', 'player_2_mana',
            'current_phase', 'turn_number', 'stack_size'
        }
        assert set(env.observation_space.spaces.keys()) == required_keys
        
        env.close()
    
    def test_action_space(self):
        """Test that action space is properly defined."""
        env = gym.make('ForgeAI-v0')
        
        # Check that action space is Discrete
        assert isinstance(env.action_space, gym.spaces.Discrete)
        
        # Check that it has reasonable size
        assert env.action_space.n == 1000
        
        env.close()
    
    def test_reset(self):
        """Test that reset returns proper observation and info."""
        env = gym.make('ForgeAI-v0')
        
        obs, info = env.reset()
        
        # Check observation structure
        assert isinstance(obs, dict)
        assert 'player_1_life' in obs
        assert 'player_2_life' in obs
        
        # Check info structure
        assert isinstance(info, dict)
        assert 'episode_step' in info
        assert info['episode_step'] == 0
        
        env.close()
    
    def test_step(self):
        """Test that step returns proper values."""
        env = gym.make('ForgeAI-v0')
        env.reset()
        
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Check return types
        assert isinstance(obs, dict)
        assert isinstance(reward, (int, float))
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
        
        env.close()
    
    def test_observation_in_space(self):
        """Test that observations are within the defined space."""
        env = gym.make('ForgeAI-v0')
        obs, _ = env.reset()
        
        # Check that observation is in the observation space
        assert env.observation_space.contains(obs)
        
        # Take a step and check again
        action = env.action_space.sample()
        obs, _, _, _, _ = env.step(action)
        assert env.observation_space.contains(obs)
        
        env.close()
    
    def test_multiple_episodes(self):
        """Test running multiple episodes."""
        env = gym.make('ForgeAI-v0')
        
        for episode in range(3):
            obs, info = env.reset()
            assert info['episode_step'] == 0
            
            for step in range(10):
                action = env.action_space.sample()
                obs, reward, terminated, truncated, info = env.step(action)
                
                if terminated or truncated:
                    break
        
        env.close()
    
    def test_render_ansi(self):
        """Test ANSI rendering mode."""
        env = gym.make('ForgeAI-v0', render_mode='ansi')
        env.reset()
        
        # Should not raise an exception
        env.render()
        
        env.close()


class TestForgeEnvValues:
    """Test that environment values are reasonable."""
    
    def test_initial_life_totals(self):
        """Test that players start with standard life totals."""
        env = gym.make('ForgeAI-v0')
        obs, _ = env.reset()
        
        # In MTG, standard starting life is 20
        assert obs['player_1_life'][0] == 20
        assert obs['player_2_life'][0] == 20
        
        env.close()
    
    def test_initial_hand_size(self):
        """Test that players start with standard hand size."""
        env = gym.make('ForgeAI-v0')
        obs, _ = env.reset()
        
        # Standard starting hand is 7
        assert obs['player_1_hand_size'][0] == 7
        assert obs['player_2_hand_size'][0] == 7
        
        env.close()
    
    def test_turn_number_starts_at_one(self):
        """Test that turn number starts at 1."""
        env = gym.make('ForgeAI-v0')
        obs, _ = env.reset()
        
        assert obs['turn_number'][0] == 1
        
        env.close()


if __name__ == '__main__':
    # Run tests if executed directly
    pytest.main([__file__, '-v'])
