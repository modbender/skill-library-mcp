#!/usr/bin/env python3
"""
Quick Training Script for Agent Lightning
Save as: train_agent.py

Usage:
    python train_agent.py --config config.yaml
"""

import argparse
import yaml
from agentlightning import Agent, RLConfig, GRPOTrainer


def load_config(config_path: str) -> dict:
    """Load training configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_agent(config: dict) -> Agent:
    """Create agent from config."""
    agent_config = config.get('agent', {})
    return Agent(
        name=agent_config.get('name', 'my-agent'),
        model=agent_config.get('model', 'gpt-4o'),
        system_prompt=agent_config.get('system_prompt', ''),
    )


def train_agent(agent: Agent, config: dict):
    """Train agent using GRPO algorithm."""
    training_config = config.get('training', {})
    
    rl_config = RLConfig(
        algorithm=training_config.get('algorithm', 'grpo'),
        episodes=training_config.get('episodes', 100),
        batch_size=training_config.get('batch_size', 8),
        learning_rate=training_config.get('learning_rate', 1e-4),
        max_steps=training_config.get('max_steps', 10000),
        checkpoint_interval=training_config.get('checkpoint_interval', 20),
        save_path=training_config.get('save_path', './checkpoints'),
    )
    
    trainer = GRPOTrainer(config=rl_config)
    
    # Get evaluation tasks
    eval_tasks = []
    env_config = config.get('environment', {})
    for task in env_config.get('eval_tasks', []):
        eval_tasks.append(task.get('name'))
    
    # Run training
    trainer.train(agent, eval_tasks=eval_tasks)
    
    # Save final model
    trainer.save("./trained-agent")


def main():
    parser = argparse.ArgumentParser(description='Train agent with Agent Lightning')
    parser.add_argument('--config', '-c', default='config.yaml',
                        help='Path to config file')
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    print(f"Loaded config from: {args.config}")
    
    # Create agent
    agent = create_agent(config)
    print(f"Created agent: {agent.name}")
    
    # Train
    print("Starting training...")
    train_agent(agent, config)
    print("Training complete!")


if __name__ == '__main__':
    main()
