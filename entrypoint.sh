#!/bin/sh
set -e

echo "[entrypoint] Esperando a que PostgreSQL este listo..."
until pg_isready -h db -U vmdocs -d vmdocs; do
  sleep 1
done
echo "[entrypoint] PostgreSQL listo."

echo "[entrypoint] Ejecutando seed de datos de demo..."
python seed.py
echo "[entrypoint] Seed completado."

echo "[entrypoint] Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
