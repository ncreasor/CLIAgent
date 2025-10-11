#!/usr/bin/env python3
"""Quick test for agent tool calling"""
import os
import sys
os.environ["OLLAMA_NO_GPU"] = "true"

# Add parent dir to path
sys.path.insert(0, os.path.dirname(__file__))

from core.agent import Agent
import json

# Load config
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Create agent
agent = Agent(config)

# Test queries
test_queries = [
    "кто ты?",
    "опиши структуру",
    "list files in this project"
]

for query in test_queries:
    print(f"\n{'='*50}")
    print(f"Query: {query}")
    print('='*50)
    response = agent.process(query)
    print(f"Response: {response}\n")
