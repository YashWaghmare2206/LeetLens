#!/usr/bin/env bash
cd backend
source venv/bin/activate || echo "No venv found, using system Python"
uvicorn app.main:app --reload
