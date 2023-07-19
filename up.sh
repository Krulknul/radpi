#!/bin/bash
if [ ! -d "venv" ]; then
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi
source venv/bin/activate
source .env
export DISPLAY=:0.0
python src/app.py