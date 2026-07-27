#!/bin/bash
# preparar_puesto.sh — deja un puesto Debian 13 recién instalado listo para el curso
# Uso:  sudo bash aula/preparar_puesto.sh [usuario]
# (usuario por defecto: el que invoca sudo)
set -e
USUARIO="${1:-${SUDO_USER:-$USER}}"
echo "== Preparación de puesto · Big Data e IA Aplicada · usuario: $USUARIO =="

echo "== 1/4 Paquetes base =="
apt-get update
apt-get install -y curl git unzip jq python3 ca-certificates

echo "== 2/4 Docker (script oficial: incluye compose) =="
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi
usermod -aG docker "$USUARIO"

echo "== 3/4 Comprobación de Docker =="
docker run --rm hello-world >/dev/null && echo "OK: docker funciona"

echo "== 4/4 Radiografía del puesto =="
echo "Arquitectura: $(uname -m)   (x86_64 = HDFS didáctico OK; aarch64 = HDFS no disponible)"
free -h | sed -n '2p'
df -h / | tail -1
echo
echo "SIGUIENTE (como $USUARIO, tras CERRAR SESIÓN Y VOLVER A ENTRAR para activar el grupo docker):"
echo "  git clone <URL-del-repositorio>   (o unzip curso-bigdata-ia.zip)"
echo "  cd curso-bigdata-ia"
echo "  python3 generar_datasets.py && bash verificacion.sh    # esperado: 28 OK · 0 FALLOS"
echo "  PRIMER PUESTO:  docker compose pull   y después exportar imágenes (ver aula/IMAGENES_USB.md)"
echo "  RESTO:          docker load -i imagenes-curso.tar"
echo "  docker compose up -d && docker compose ps               # jupyter+namenode+datanode Up"
