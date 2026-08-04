#!/bin/bash
# preparar_bloque2.sh — deja el HOST listo para el BLOQUE 2 (SQL, JOINs y Spark)
# Formación San Miguel · Big Data e IA Aplicada · Edición Técnica
#
# Uso:  bash aula/preparar_bloque2.sh [opciones]
#
#   --sin-venv      instala duckdb en el Python del sistema con --break-system-packages
#                   en vez de crear un entorno aislado (más rápido, ensucia el sistema)
#   --sin-docker    no toca los contenedores (útil si preparas solo los datos)
#   --regenerar     regenera los datasets aunque ya existan y midan lo que deben
#   --ayuda         esto
#
# QUÉ HACE Y POR QUÉ:
#   El bloque 1 se verificaba con shell (awk, grep): funciona en cualquier host.
#   El bloque 2 se verifica con SU herramienta, DuckDB vía Python — y ahí aparece la
#   avería del día: `pip install duckdb` en la terminal de JupyterLab instala DENTRO
#   del contenedor, así que el host sigue sin verlo y verificacion_b2.sh canta
#   ModuleNotFoundError. Este script prepara los DOS sitios, cada uno por su vía.
#
#   No borra nada, no toca tus cuadernos y se puede volver a ejecutar tantas veces
#   como quieras: cada paso comprueba antes de actuar.
#
# NO usa `set -e` a propósito: es un script de diagnóstico. Preferimos llegar al
# final con el recuento de fallos delante que morir en el primero y no saber qué más
# había roto.

export LC_ALL=C

VENV="$HOME/.venv-curso"
USAR_VENV=1
USAR_DOCKER=1
REGENERAR=0

for arg in "$@"; do
  case "$arg" in
    --sin-venv)   USAR_VENV=0 ;;
    --sin-docker) USAR_DOCKER=0 ;;
    --regenerar)  REGENERAR=1 ;;
    --ayuda|-h)   sed -n '2,25p' "$0"; exit 0 ;;
    *) echo "Opción desconocida: $arg  (prueba --ayuda)"; exit 2 ;;
  esac
done

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ" || { echo "No encuentro la raíz del repositorio."; exit 1; }

OK=0; FALLO=0; AVISO=0
paso ()  { echo; echo "== $1 =="; }
bien ()  { OK=$((OK+1));       echo "  OK     $1"; }
mal ()   { FALLO=$((FALLO+1)); echo "  FALLO  $1"; }
ojo ()   { AVISO=$((AVISO+1)); echo "  AVISO  $1"; }

echo "== Preparación del BLOQUE 2 · $(date '+%Y-%m-%d %H:%M') =="
echo "   repositorio: $RAIZ"

# ---------------------------------------------------------------------------
paso "1/7 · El repositorio está donde debe"
# ---------------------------------------------------------------------------
for f in generar_datasets.py verificacion.sh docker-compose.yml; do
  [ -f "$f" ] && bien "existe $f" || mal "falta $f — ¿estás en la carpeta del curso?"
done
[ "$FALLO" -gt 0 ] && { echo; echo "Sin el repositorio completo no sigo."; exit 1; }

# ---------------------------------------------------------------------------
paso "2/7 · Sincronizar con el remoto"
# ---------------------------------------------------------------------------
if [ ! -d .git ]; then
  ojo "esto no es un clon de git (vía zip). Salta el pull: descomprime el zip nuevo aparte
         y copia encima SOLO lo nuevo, como dice aula/ACTUALIZAR.md"
elif ! command -v git >/dev/null 2>&1; then
  mal "git no está instalado:  sudo apt install -y git"
else
  # La regla de oro del curso: los originales se copian antes de editarse. Si aun así
  # hay cambios locales, avisamos y NO tocamos nada: perder el trabajo de un alumno
  # por un script automático sería mucho peor que un pull pendiente.
  if [ -n "$(git status --porcelain -- notebooks aula plantillas docs 2>/dev/null)" ]; then
    ojo "tienes cambios locales en ficheros del curso. NO hago pull para no pisártelos."
    echo "         Salva tu trabajo y restaura los originales:"
    echo "           cp notebooks/lab06_lab07.ipynb notebooks/mi_lab06_salvado.ipynb"
    echo "           git checkout -- notebooks/ && git pull"
  elif git pull --ff-only >/dev/null 2>&1; then
    bien "git pull al día ($(git rev-parse --short HEAD))"
  else
    ojo "el git pull no ha entrado limpio. Hazlo a mano y mira qué dice"
  fi
fi

# ---------------------------------------------------------------------------
paso "3/7 · Los cuadernos del bloque 2"
# ---------------------------------------------------------------------------
# Se agrupan por SESIÓN, no por laboratorio: el ancla del LAB06 y la sesión de Spark
# viven en el kernel, y separarlas en ficheros obligaría a reconstruirlas una y otra vez.
for nb in notebooks/lab06_lab07.ipynb notebooks/lab08_lab09_lab10.ipynb; do
  [ -f "$nb" ] && bien "existe $nb" || mal "falta $nb — ¿el pull ha traído el bloque 2?"
done
# Un cuaderno suelto llamado lab06.ipynb hace que la celda de archivado (que busca por
# patrón) encuentre un fichero vacío y se niegue a archivar. Es una avería real.
for suelto in notebooks/lab06.ipynb notebooks/lab07.ipynb notebooks/lab08.ipynb; do
  [ -f "$suelto" ] && ojo "sobra $suelto: la celda de archivado busca por patrón y este
         cuaderno suelto puede hacer que se niegue a archivar. Bórralo o renómbralo"
done

# ---------------------------------------------------------------------------
paso "4/7 · Los datasets"
# ---------------------------------------------------------------------------
# Semilla fija (random.seed(2026)): todos los puestos fabrican bytes idénticos. Por eso
# el tamaño exacto de ventas.csv sirve como huella: si no son estos bytes, no son estos datos.
HUELLA=61942187
TAM=$(stat -c%s datasets/ventas.csv 2>/dev/null || echo 0)

if [ "$REGENERAR" = 1 ] || [ ! -f datasets/ventas.csv ] || [ "$TAM" != "$HUELLA" ]; then
  [ "$TAM" != 0 ] && [ "$TAM" != "$HUELLA" ] && ojo "ventas.csv mide $TAM bytes y debería medir $HUELLA: lo regenero"
  echo "  generando los cuatro datasets (1-3 min)..."
  if python3 generar_datasets.py; then
    bien "datasets generados"
  else
    mal "generar_datasets.py ha fallado"
  fi
else
  bien "datasets ya presentes y con la huella correcta ($HUELLA bytes)"
fi

# El LAB08 publica su primer entregable de datos aquí (COPY ... TO). La celda la crea,
# pero tenerla ya hecha evita el susto de un permiso raro en mitad de la clase.
mkdir -p datasets/salida && bien "datasets/salida/ preparada (la carpeta oficial de resultados)"

# ---------------------------------------------------------------------------
paso "5/7 · duckdb en el HOST (para verificacion_b2.sh)"
# ---------------------------------------------------------------------------
# verificacion_b2.sh hace `python3 - <<PY`, así que necesita el intérprete que resuelva
# el PATH. En Debian 13 y Ubuntu 24 el Python del sistema está marcado como
# "externally managed" (PEP 668) y pip se niega a instalar sin permiso explícito.
PY_HOST="python3"

if python3 -c "import duckdb" 2>/dev/null; then
  bien "el python3 del sistema ya ve duckdb ($(python3 -c 'import duckdb; print(duckdb.__version__)'))"
elif [ "$USAR_VENV" = 1 ]; then
  if [ ! -x "$VENV/bin/python" ]; then
    echo "  creando entorno aislado en $VENV ..."
    python3 -m venv "$VENV" 2>/dev/null || {
      mal "no he podido crear el venv:  sudo apt install -y python3-venv"; }
  fi
  if [ -x "$VENV/bin/python" ]; then
    # --only-binary evita que se ponga a compilar duckdb desde fuente: con rueda son
    # segundos; compilando son muchos minutos y no queremos eso a las 16:30.
    "$VENV/bin/pip" install --quiet --only-binary=:all: duckdb \
      && bien "duckdb instalado en el entorno aislado ($("$VENV/bin/python" -c 'import duckdb; print(duckdb.__version__)'))" \
      || mal "pip no ha podido instalar duckdb en el venv"
    PY_HOST="$VENV/bin/python"
  fi
else
  if ! command -v pip3 >/dev/null 2>&1 && ! python3 -m pip --version >/dev/null 2>&1; then
    ojo "no hay pip:  sudo apt install -y python3-pip"
  fi
  python3 -m pip install --quiet --break-system-packages --only-binary=:all: duckdb \
    && bien "duckdb instalado en el Python del sistema" \
    || mal "pip no ha podido instalar duckdb (prueba sin --sin-venv, o mira el mensaje completo)"
fi

# ---------------------------------------------------------------------------
paso "6/7 · Los dos jueces"
# ---------------------------------------------------------------------------
# El del bloque 1 es shell puro y corre en cualquier host. El del bloque 2 lleva
# embebida la definición canónica LIMPIO-v1: es la fuente de verdad de que tu ancla
# es LA ancla.
command -v jq >/dev/null 2>&1 || ojo "falta jq: las 7 comprobaciones del catálogo del LAB04
         van a fallar y NO son los datos.  sudo apt install -y jq"

if [ -f verificacion.sh ]; then
  R=$(bash verificacion.sh 2>/dev/null | tail -1)
  if echo "$R" | grep -q "28 OK"; then
    bien "verificacion.sh -> 28 OK · 0 FALLOS"
  elif ! command -v jq >/dev/null 2>&1 && echo "$R" | grep -q "7 FALLOS"; then
    ojo "verificacion.sh -> [$R]. Son EXACTAMENTE los 7 del catálogo: es jq, no los datos"
  else
    mal "verificacion.sh no da 28 OK -> [$R]"
  fi
fi

if [ ! -f verificacion_b2.sh ]; then
  mal "falta verificacion_b2.sh — no ha llegado el paquete del bloque 2"
else
  # Con el venv activado, el `python3` del heredoc pasa a ser el del entorno: por eso
  # anteponemos su bin al PATH en vez de editar el script.
  R=$(PATH="$(dirname "$PY_HOST"):$PATH" bash verificacion_b2.sh 2>&1 | tail -1)
  if echo "$R" | grep -q "16 OK"; then
    bien "verificacion_b2.sh -> $R"
  else
    mal "verificacion_b2.sh -> [$R]"
  fi
fi

# ---------------------------------------------------------------------------
paso "7/7 · Los contenedores y el duckdb del AULA"
# ---------------------------------------------------------------------------
if [ "$USAR_DOCKER" = 0 ]; then
  ojo "paso omitido por --sin-docker"
elif ! command -v docker >/dev/null 2>&1; then
  mal "docker no está:  sudo bash aula/preparar_puesto.sh"
else
  docker compose up -d >/dev/null 2>&1
  if docker compose ps --status running 2>/dev/null | grep -q jupyter; then
    bien "jupyter levantado"
    # ESTA es la línea que evita quince manos levantadas en el minuto tres: duckdb
    # dentro del contenedor, que es donde vive el kernel de los alumnos.
    if docker compose exec -T jupyter python3 -c "import duckdb" 2>/dev/null; then
      bien "el contenedor ya tiene duckdb ($(docker compose exec -T jupyter python3 -c 'import duckdb; print(duckdb.__version__)' 2>/dev/null | tr -d '\r'))"
    else
      echo "  instalando duckdb dentro del contenedor..."
      docker compose exec -T jupyter pip install --quiet duckdb >/dev/null 2>&1
      docker compose exec -T jupyter python3 -c "import duckdb" 2>/dev/null \
        && bien "duckdb instalado en el contenedor" \
        || mal "no he podido instalar duckdb en el contenedor"
    fi
    ojo "recuerda: un 'docker compose down' se lleva por delante ese duckdb.
         Si apagas los contenedores, vuelve a pasar este script antes de clase"
  else
    mal "jupyter no está Up — mira 'docker compose logs jupyter'"
  fi
fi

# ---------------------------------------------------------------------------
echo
echo "=================================================================="
echo " RESULTADO:  $OK OK · $FALLO FALLOS · $AVISO avisos"
echo "=================================================================="

if [ "$FALLO" = 0 ]; then
cat <<'FIN'

 El host está listo para el bloque 2. Lo que queda es tuyo:

   [ ] Abrir JupyterLab y ejecutar lab04_lab05.ipynb ENTERO, cronometrando la
       conversión a Parquet: necesitas TU tiempo de CSV y TU tiempo de Parquet
       para decirlos en voz alta (la ratio es un rango, 9-18x, nunca una cifra)
   [ ] Ejecutar lab06_lab07.ipynb con Restart & Run All: el ancla tiene que dar
       999.535 filas · 429.892.547,06 EUR · ticket 430,09
   [ ] Decidir el valor de SESION en las DOS celdas de archivado y anotarlo en
       la pizarra: lo único que no puede pasar es que cada puesto lleve un número
   [ ] Abrir las tareas de Moodle

 Y la avería del aula que no está en ningún manual: donde la documentación dice
 localhost, aquí es LA IP DE LA VM. El localhost del alumno es su Windows, no la
 máquina donde corren los servicios.

FIN
else
  echo
  echo " Revisa los FALLO de arriba antes de clase. Si el que falla es solo"
  echo " verificacion_b2.sh, no es un bloqueo: el aula instala duckdb dentro de"
  echo " Jupyter, que además es la lección del laboratorio. El juez es comodidad tuya."
  echo
fi

exit $((FALLO > 0))
