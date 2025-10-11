#!/usr/bin/env python3
"""Quick single query test"""
import os
import sys
os.environ["OLLAMA_NO_GPU"] = "true"

sys.path.insert(0, os.path.dirname(__file__))

from core.agent import Agent
import json

# Load config
with open('config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Create agent
print("Creating agent...")
agent = Agent(config)

# Single test
query = "list files"
print(f"\nQuery: {query}")
print("="*50)

try:
    response = agent.process(query)
    print(f"Response:\n{response}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
