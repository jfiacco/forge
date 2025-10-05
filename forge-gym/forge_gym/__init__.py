"""Forge Gymnasium Environment for Magic: The Gathering AI."""

from gymnasium.envs.registration import register

from forge_gym.envs.forge_env import ForgeEnv

__version__ = "0.1.0"

# Register the environment with Gymnasium
register(
    id='ForgeAI-v0',
    entry_point='forge_gym.envs:ForgeEnv',
    max_episode_steps=10000,  # Max turns per game
)

__all__ = ['ForgeEnv']
