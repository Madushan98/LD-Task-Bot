#!/bin/bash

# Detect if running on Windows Git Bash
if [[ "$OSTYPE" == "msys" ]]; then
  source venv/Scripts/activate
else
  source venv/bin/activate
fi
uvicorn app.main:app --reload