#!/usr/bin/env bash
# Run both backend and frontend

trap 'kill %1; kill %2' SIGINT

./run_backend.sh &
BACKEND_PID=$!

./run_frontend.sh &
FRONTEND_PID=$!

wait
