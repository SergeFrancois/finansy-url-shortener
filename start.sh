#!/bin/bash
venv/bin/uvicorn finansy.url_shortener.main:app --app-dir src --host 0.0.0.0 --port 5001&
PID="$!"
trap "kill $PID; wait $PID" SIGTERM SIGKILL 
wait