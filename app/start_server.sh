#!/bin/bash
cd "$(dirname "$0")"

echo "Starting mudac emotions server"
python3 app_service.py
