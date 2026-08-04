#!/bin/bash
# preparar_bloque2.sh — deja el HOST listo para el BLOQUE 2 (SQL, JOINs y Spark)
# Formación San Miguel · Big Data e IA Aplicada · Edición Técnica · rev. 2
#
# Uso:  bash aula/preparar_bloque2.sh [opciones]
#
#   --forzar-pull   si hay cambios locales, los guarda en un `git stash` con nombre
#                   y hace el pull. NADA se pierde: se recupera con `git stash pop`
#   --sin-docker    no toca los contenedores
#   --regenerar     regenera los datasets aunque ya existan y tengan la huella buena
#   --ayuda         esto
#
# QUÉ HACE Y POR QUÉ
#   El bloque 1 se verificaba con shell (awk, grep) y por eso corre en cualquier host.
#   El bloque 2 se verifica con SU herramienta, DuckDB vía Python, y ahí aparece la
#   avería del día: `pip install duckdb` en la terminal de JupyterLab instala DENTRO
#   del contenedor, así que el host sigue sin verlo y verificacion_b2.sh canta
#   ModuleNotFoundError.
#
#   Este script NO se limita a diagnosticar: intenta arreglarlo solo, probando las
#   vías por orden de menos invasiva a más, y sin pedir sudo salvo que ya lo tengas
#   sin contraseña. Si ninguna vía funciona, todavía tiene un as: el contenedor YA
#   lleva duckdb, así que pasa el juez ahí dentro y te da igualmente los 16 números.
#
#   No borra nada tuyo, no toca tus cuadernos y se puede repetir tantas veces como
#   quieras: cada paso comprueba antes de actuar.
#
# NO usa `set -e` a propósito: es un script de reparación. Preferimos llegar al final
# con el recuento delante que morir en el primer fallo sin saber qué más había roto.

export LC_ALL=C

VENV="$HOME/.venv-curso"
FORZAR_PULL=0
USAR_DOCKER=1
REGENERAR=0

for arg in "$@"; do
  case "$arg" in
    --forzar-pull) FORZAR_PULL=1 ;;
    --sin-docker)  USAR_DOCKER=0 ;;
    --regenerar)   REGENERAR=1 ;;
    --ayuda|-h)    sed -n '2,30p' "$0"; exit 0 ;;
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
hago ()  { echo "  ...    $1"; }

# ¿tenemos sudo sin contraseña? Solo entonces instalamos paquetes por nuestra cuenta:
# un script que se queda esperando una contraseña delante de quince alumnos es peor
# que un script que te dice qué escribir.
SUDO=""
sudo -n true 2>/dev/null && SUDO="sudo -n"

echo "== Preparación del BLOQUE 2 · rev. 2 · $(date '+%Y-%m-%d %H:%M') =="
echo "   repositorio: $RAIZ"
[ -n "$SUDO" ] && echo "   sudo sin contraseña: disponible (podré instalar paquetes yo)"

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
  ojo "esto no es un clon de git (vía zip): descomprime el zip nuevo aparte y copia
         encima solo lo nuevo, como dice aula/ACTUALIZAR.md"
elif ! command -v git >/dev/null 2>&1; then
  mal "git no está instalado:  sudo apt install -y git"
elif [ -z "$(git status --porcelain -- notebooks aula plantillas docs 2>/dev/null)" ]; then
  git pull --ff-only >/dev/null 2>&1 \
    && bien "git pull al día ($(git rev-parse --short HEAD))" \
    || ojo "el git pull no ha entrado limpio. Hazlo a mano y mira qué dice"
elif [ "$FORZAR_PULL" = 1 ]; then
  # Reversible por diseño: el stash lleva fecha en el mensaje y se recupera entero.
  ETIQUETA="preparar_bloque2 $(date '+%Y-%m-%d %H:%M')"
  if git stash push -u -m "$ETIQUETA" -- notebooks aula plantillas docs >/dev/null 2>&1; then
    hago "tus cambios locales están guardados en el stash: «$ETIQUETA»"
    git pull --ff-only >/dev/null 2>&1 \
      && bien "git pull hecho. Recupera tu trabajo cuando quieras con:  git stash pop" \
      || ojo "el pull sigue sin entrar. Tu trabajo está a salvo:  git stash list"
  else
    ojo "no he podido guardar tus cambios en el stash. No hago pull"
  fi
else
  ojo "tienes cambios locales en ficheros del curso. NO hago pull para no pisártelos.
         Si quieres que me encargue yo (los guarda en un stash, no se pierde nada):
           bash aula/preparar_bloque2.sh --forzar-pull"
fi

# ---------------------------------------------------------------------------
paso "3/7 · Los cuadernos del bloque 2"
# ---------------------------------------------------------------------------
# Van agrupados por SESIÓN, no por laboratorio: el ancla del LAB06 y la sesión de Spark
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
# Semilla fija (random.seed(2026)): todos los puestos fabrican bytes idénticos, así que
# el tamaño exacto de ventas.csv vale como huella. Si no son estos bytes, no son estos datos.
HUELLA=61942187
TAM=$(stat -c%s datasets/ventas.csv 2>/dev/null || echo 0)

if [ "$REGENERAR" = 1 ] || [ ! -f datasets/ventas.csv ] || [ "$TAM" != "$HUELLA" ]; then
  [ "$TAM" != 0 ] && [ "$TAM" != "$HUELLA" ] && ojo "ventas.csv mide $TAM bytes y debería medir $HUELLA: lo regenero"
  hago "generando los cuatro datasets (1-3 min)"
  python3 generar_datasets.py >/dev/null && bien "datasets generados" || mal "generar_datasets.py ha fallado"
else
  bien "datasets presentes y con la huella correcta ($HUELLA bytes)"
fi

# El LAB08 publica aquí su primer entregable de datos (COPY ... TO). La celda la crea,
# pero tenerla hecha evita el susto de un permiso raro en mitad de la clase.
mkdir -p datasets/salida && bien "datasets/salida/ preparada (la carpeta oficial de resultados)"

# `jq` lo necesitan las 7 comprobaciones del catálogo del LAB04 dentro de verificacion.sh.
if ! command -v jq >/dev/null 2>&1; then
  if [ -n "$SUDO" ]; then
    hago "instalando jq"
    $SUDO apt-get install -y -qq jq >/dev/null 2>&1
  fi
  command -v jq >/dev/null 2>&1 && bien "jq instalado" \
    || ojo "falta jq: las 7 comprobaciones del catálogo van a fallar y NO son los datos.
         sudo apt install -y jq"
fi

# ---------------------------------------------------------------------------
paso "5/7 · duckdb para el juez del bloque 2"
# ---------------------------------------------------------------------------
# verificacion_b2.sh hace `python3 - <<PY`, así que necesita el intérprete que resuelva
# el PATH. En Debian 13 y Ubuntu 24 el Python del sistema está marcado como "externally
# managed" (PEP 668) y pip se niega a instalar sin permiso explícito.
#
# Probamos las vías por orden, de menos invasiva a más, y paramos en la primera que
# funcione. Cada una comprueba con un `import` de verdad: que pip diga «instalado» no
# es prueba de nada.
PY_HOST=""
MODO=""

hay_duckdb () { "$1" -c "import duckdb" 2>/dev/null; }
version_de () { "$1" -c "import duckdb; print(duckdb.__version__)" 2>/dev/null; }

# vía 0 · ya está
if hay_duckdb python3; then
  PY_HOST="python3"; MODO="sistema"
  bien "el python3 del host ya ve duckdb ($(version_de python3))"
fi

# vía 1 · ~/.local — no necesita sudo, no toca /usr, y se deshace con un pip uninstall
if [ -z "$PY_HOST" ] && python3 -m pip --version >/dev/null 2>&1; then
  hago "instalando duckdb para tu usuario (~/.local)"
  python3 -m pip install --quiet --user --break-system-packages --only-binary=:all: duckdb >/dev/null 2>&1 \
    || python3 -m pip install --quiet --user --only-binary=:all: duckdb >/dev/null 2>&1
  if hay_duckdb python3; then
    PY_HOST="python3"; MODO="usuario"
    bien "duckdb en ~/.local ($(version_de python3))"
  fi
fi

# vía 2 · entorno aislado. OJO: en Debian, `python3 -m venv` SIN el paquete python3-venv
# crea la carpeta y el enlace a bin/python, y solo después falla al llegar a ensurepip:
# queda un venv a medias, con Python y sin pip. Por eso la prueba de vida es bin/pip.
if [ -z "$PY_HOST" ]; then
  if [ -x "$VENV/bin/pip" ] || {
       [ -d "$VENV" ] && { hago "había un $VENV a medias (sin pip): lo rehago"; rm -rf "$VENV"; }
       hago "creando entorno aislado en $VENV"
       SALIDA=$(python3 -m venv "$VENV" 2>&1); [ -x "$VENV/bin/pip" ]; }; then
    "$VENV/bin/pip" install --quiet --only-binary=:all: duckdb >/dev/null 2>&1
    if hay_duckdb "$VENV/bin/python"; then
      PY_HOST="$VENV/bin/python"; MODO="venv"
      bien "duckdb en el entorno aislado ($(version_de "$VENV/bin/python"))"
    fi
  fi
fi

# vía 3 · con sudo sin contraseña, los paquetes de Debian y otra pasada por la vía 1
if [ -z "$PY_HOST" ] && [ -n "$SUDO" ]; then
  hago "instalando python3-pip y python3-venv"
  $SUDO apt-get update -qq >/dev/null 2>&1
  $SUDO apt-get install -y -qq python3-pip python3-venv >/dev/null 2>&1
  python3 -m pip install --quiet --user --break-system-packages --only-binary=:all: duckdb >/dev/null 2>&1
  if hay_duckdb python3; then
    PY_HOST="python3"; MODO="usuario"
    bien "duckdb instalado tras añadir los paquetes ($(version_de python3))"
  fi
fi

# vía 4 · el as en la manga: el contenedor YA lleva duckdb. No instalamos nada en el
# host y el juez se pasa igual, dentro de Jupyter, contra los mismos datasets montados.
if [ -z "$PY_HOST" ] && [ "$USAR_DOCKER" = 1 ] && command -v docker >/dev/null 2>&1; then
  docker compose up -d >/dev/null 2>&1
  if docker compose exec -T jupyter python3 -c "import duckdb" >/dev/null 2>&1; then
    MODO="docker"
    ojo "no he podido poner duckdb en el host, pero el contenedor sí lo tiene:
         paso el juez ahí dentro. Para el aula da exactamente igual"
  fi
fi

if [ -z "$MODO" ]; then
  mal "no he conseguido duckdb por ninguna vía. A mano, cualquiera de estas dos:
         python3 -m pip install --user --break-system-packages duckdb
         sudo apt install -y python3-venv && rm -rf $VENV && bash aula/preparar_bloque2.sh"
fi

# ---------------------------------------------------------------------------
paso "6/7 · Los dos jueces"
# ---------------------------------------------------------------------------
# El del bloque 1 es shell puro y corre en cualquier host. El del bloque 2 lleva embebida
# la definición canónica LIMPIO-v1: es la fuente de verdad de que tu ancla es LA ancla.
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
elif [ "$MODO" = "docker" ]; then
  # Se le saca el bloque de Python al script y se le da de comer al intérprete del
  # contenedor, con el directorio de trabajo en los datasets montados. Misma definición
  # de LIMPIO-v1, mismos ficheros, mismos 16 números.
  R=$(sed -n "/^python3 - <<'PY'\$/,/^PY\$/p" verificacion_b2.sh | sed '1d;$d' \
      | docker compose exec -T -w /home/jovyan/datasets jupyter python3 - 2>&1 | tail -1)
  echo "$R" | grep -q "16 OK" && bien "verificacion_b2.sh (en el contenedor) -> $R" \
                              || mal "verificacion_b2.sh (en el contenedor) -> [$R]"
elif [ -n "$PY_HOST" ]; then
  # Anteponemos el bin del intérprete bueno al PATH en vez de editar el script: el
  # `python3` del heredoc pasa a ser el nuestro y el juez queda intacto.
  # OJO: nada de `readlink -f` aquí. El bin/python de un venv es un enlace al Python
  # del sistema, así que resolverlo nos devolvería a /usr/bin y anularía el arreglo.
  if [ "$PY_HOST" = "python3" ]; then
    R=$(bash verificacion_b2.sh 2>&1 | tail -1)
  else
    R=$(PATH="$(cd "$(dirname "$PY_HOST")" && pwd):$PATH" bash verificacion_b2.sh 2>&1 | tail -1)
  fi
  echo "$R" | grep -q "16 OK" && bien "verificacion_b2.sh -> $R" || mal "verificacion_b2.sh -> [$R]"
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
    if docker compose exec -T jupyter python3 -c "import duckdb" >/dev/null 2>&1; then
      bien "el contenedor tiene duckdb ($(docker compose exec -T jupyter python3 -c 'import duckdb; print(duckdb.__version__)' 2>/dev/null | tr -d '\r'))"
    else
      hago "instalando duckdb dentro del contenedor"
      docker compose exec -T jupyter pip install --quiet duckdb >/dev/null 2>&1
      docker compose exec -T jupyter python3 -c "import duckdb" >/dev/null 2>&1 \
        && bien "duckdb instalado en el contenedor" || mal "no he podido instalarlo en el contenedor"
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
[ -n "$MODO" ] && echo " duckdb del juez: vía «$MODO»"
echo "=================================================================="

if [ "$FALLO" = 0 ]; then
cat <<'FIN'

 El host está listo para el bloque 2. Lo que queda es tuyo:

   [ ] Ejecutar lab04_lab05.ipynb ENTERO cronometrando la conversión a Parquet:
       necesitas TU tiempo de CSV y TU tiempo de Parquet para decirlos en voz alta
       (la ratio es un rango, 9-18x, nunca una cifra cerrada)
   [ ] Ejecutar lab06_lab07.ipynb con Restart & Run All: el ancla tiene que dar
       999.535 filas · 429.892.547,06 EUR · ticket 430,09
   [ ] Decidir el valor de SESION en las DOS celdas de archivado y anotarlo en la
       pizarra: lo único que no puede pasar es que cada puesto lleve un número
   [ ] Abrir las tareas de Moodle

 Y la avería del aula que no está en ningún manual: donde la documentación dice
 localhost, aquí es LA IP DE LA VM. El localhost del alumno es su Windows, no la
 máquina donde corren los servicios.

FIN
else
  echo
  echo " Revisa los FALLO de arriba. Si el único que queda es verificacion_b2.sh,"
  echo " no es un bloqueo: el aula instala duckdb dentro de Jupyter, que además es"
  echo " la lección del laboratorio. El juez es una comodidad tuya."
  echo
fi

exit $((FALLO > 0))
