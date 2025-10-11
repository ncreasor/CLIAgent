#!/usr/bin/env python3
"""Simplest possible test"""
import sys
print("Test starting...", flush=True)

import os
os.environ["OLLAMA_NO_GPU"] = "true"

sys.path.insert(0, os.path.dirname(__file__))

print("Importing modules...", flush=True)
from core.agent import Agent
import json

print("Loading config...", flush=True)
with open('config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

print("Creating agent...", flush=True)
agent = Agent(config)

query = "hello"
print(f"\nSending query: {query}", flush=True)
print("="*50, flush=True)

try:
    response = agent.process(query)
    print(f"\nGot response:\n{response}", flush=True)
except KeyboardInterrupt:
    print("\nInterrupted by user", flush=True)
except Exception as e:
    print(f"\nERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("\nTest done.", flush=True)
