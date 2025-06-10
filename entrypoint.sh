#!/bin/sh

echo ">> Running Alembic migrations..."
alembic upgrade head

echo ">> Starting Uvicorn..."
if [ "$ENVIRONMENT" = "production" ]; then
    uvicorn app.main:app --host 0.0.0.0 --port 80
else
    uvicorn app.main:app --host 0.0.0.0 --port 80 --reload
fi
