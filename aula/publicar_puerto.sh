#!/usr/bin/env bash
# Publica el puerto 8501 en el servicio de Jupyter, sin tocar el compose original.
# Uso:   bash aula/publicar_puerto.sh [nombre_del_servicio]
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"

echo "  Servicios definidos en tu compose:"
docker compose config --services | sed 's/^/    /'
echo

SERVICIO="${1:-}"
if [ -z "$SERVICIO" ]; then
  SERVICIO="$(docker compose config --services | grep -i -m1 -E 'jupyter|lab|notebook' || true)"
fi
if [ -z "$SERVICIO" ]; then
  echo "  No he sabido cual es el de Jupyter. Vuelve a lanzarlo con el nombre:"
  echo "     bash aula/publicar_puerto.sh <servicio>"
  exit 1
fi
echo "  Servicio elegido: $SERVICIO"

if docker compose config | grep -q '8501'; then
  echo "  El puerto 8501 YA esta publicado. No hay nada que hacer."
  exit 0
fi

sed "s/^  jupyter:/  $SERVICIO:/" aula/docker-compose.override.yml > docker-compose.override.yml
echo "  Escrito docker-compose.override.yml:"
sed 's/^/    /' docker-compose.override.yml
echo
echo "  Recreando el contenedor (los cuadernos viven en el volumen y no se tocan)..."
docker compose up -d
echo
docker compose ps
echo
echo "  Listo. La app se abrira en  http://IP-DE-LA-VM:8501"
echo "  Para deshacerlo:  rm docker-compose.override.yml && docker compose up -d"
