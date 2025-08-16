@echo off
if not exist venv (
    python -m venv venv
)
"venv/Scripts/pip" install .