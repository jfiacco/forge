"""
Basic usage example for the Forge Gymnasium environment.

This demonstrates how to use the ForgeEnv with a simple random agent.
Note: This is a skeleton and will need a complete implementation of the
Java-Python bridge to actually work.
"""

import gymnasium as gym
import forge_gym


def random_agent_example():
    """Run a simple random agent in the Forge environment."""
    
    # Create the environment
    env = gym.make('ForgeAI-v0', render_mode='ansi')
    
    # Reset to start a new game
    observation, info = env.reset()
    print("Game started!")
    print(f"Initial observation: {observation}")
    
    # Run for a few steps with random actions
    total_reward = 0
    step = 0
    done = False
    
    while not done and step < 100:
        # Sample a random action
        action = env.action_space.sample()
        
        # Take a step
        observation, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        total_reward += reward
        step += 1
        
        # Render the current state
        env.render()
        
        print(f"Step {step}: action={action}, reward={reward}, done={done}")
    
    print(f"\nGame ended after {step} steps with total reward: {total_reward}")
    
    # Clean up
    env.close()


def train_example():
    """
    Example of how you might integrate with a RL library like stable-baselines3.
    
    This is pseudocode - stable-baselines3 would need to be installed and
    the environment would need to be fully implemented.
    """
    print("\nTraining example (pseudocode):")
    print("""
    from stable_baselines3 import PPO
    import forge_gym
    
    # Create the environment
    env = gym.make('ForgeAI-v0')
    
    # Create the agent
    model = PPO('MultiInputPolicy', env, verbose=1)
    
    # Train the agent
    model.learn(total_timesteps=100000)
    
    # Save the trained model
    model.save('forge_ppo_agent')
    
    # Test the trained agent
    obs, info = env.reset()
    for _ in range(1000):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            obs, info = env.reset()
    
    env.close()
    """)


if __name__ == "__main__":
    print("=" * 60)
    print("Forge Gymnasium Environment - Basic Usage Example")
    print("=" * 60)
    print("\nNote: This is a skeleton implementation.")
    print("The Java-Python bridge needs to be implemented for actual gameplay.\n")
    
    # Run random agent example
    random_agent_example()
    
    # Show training pseudocode
    train_example()
