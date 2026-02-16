#!/usr/bin/env bash
python3 -m uvicorn backend.main:app --reload --reload-dir backend --port 8000 --host 0.0.0.0
