#!/bin/bash

echo "Starting LLM service..."
uvicorn service_llm:app --host 0.0.0.0 --port 4321 --workers 1

