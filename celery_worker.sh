#!/bin/bash

# Activate venv
if [[ "$OSTYPE" == "msys" ]]; then
  source venv/Scripts/activate
else
  source venv/bin/activate
fi

# Run beat in background
celery -A celery_worker beat --loglevel=info &

# Run worker in foreground
celery -A celery_worker worker --loglevel=info --pool=solo