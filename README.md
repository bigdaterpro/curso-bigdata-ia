# curso-bigdata-ia · Bloques 1–2

Repositorio ejecutable del curso **Big Data e Inteligencia Artificial Aplicada — Edición
Técnica** (Formación San Miguel · Zaragoza · 40 h). Una descarga = entorno + datos +
cuadernos + material.

> **Ni los manuales del alumno ni la rúbrica viajan en este repositorio: están en Moodle.**
> Aquí solo vive lo ejecutable. Si algo de aquí contradice al manual del Bloque 1, manda la
> **hoja de erratas** de Moodle. Los manuales 2 y 3 ya salen corregidos.

## Puesta en marcha (LAB01)

> ¿Puesto Debian recién instalado? Primero `sudo bash aula/preparar_puesto.sh` (instala git,
> jq y Docker) y cierra/abre sesión.

```bash
cd curso-bigdata-ia
python3 generar_datasets.py     # ~1-3 min: fabrica los 4 datasets en ./datasets/
docker compose up -d            # la 1ª vez descarga imágenes; después, segundos
docker compose ps               # jupyter, namenode y datanode deben estar Up
```

Abre **http://IP-DE-LA-VM:8888** (token: `curso`). En la terminal de JupyterLab:

```bash
ls -lh datasets/
# -rw-r--r-- 60M  ventas.csv      · 1.000.000 ventas
# -rw-r--r-- 4,7M clientes.csv    · 100.000 clientes
# -rw-r--r-- 98K  productos.json  · 480 productos
# -rw-r--r-- 42M  access.log      · 500.000 líneas de servidor web
```

> ⚠️ Donde el manual diga `localhost`, en el aula es **la IP de la VM**: tu `localhost` es tu
> Windows, no la máquina donde corren los servicios.

### Al empezar el Bloque 2

```bash
bash aula/prepararb2.sh
```

Sincroniza el repositorio, comprueba que están los cuadernos del bloque, genera los datasets si
faltan, **instala duckdb donde haga falta** —en el host para el juez y dentro del contenedor para
el aula—, levanta los servicios y pasa las dos verificaciones. Termina con un recuento
`N OK · N FALLOS · N avisos` y no toca nada tuyo: si encuentra cambios locales, avisa en vez de
pisarlos. Se puede repetir tantas veces como quieras.

## Los datos: semilla fija 2026

`generar_datasets.py` usa `random.seed(2026)`: **todos los puestos generan datos idénticos** y
tus resultados deben coincidir con los de los manuales. La suciedad de los datasets y el patrón
anómalo del log están plantados a propósito: son parte de los ejercicios. **No modifiques el
script** (si quieres experimentar, cópialo con otro nombre y otra carpeta de salida).

`verificacion.sh` contrasta los datasets con los valores del bloque 1: **28 OK**. Requiere `jq`.
`verificacion_b2.sh` hace lo propio con los **16 números del bloque 2** — y lleva embebida la
**definición canónica LIMPIO-v1**: `bash verificacion_b2.sh` → **16 OK · 0 FALLOS**. Necesita
DuckDB, pero **se busca solo un Python que lo tenga**: primero el del `PATH`, después
`~/.venv-curso/bin/python`, y si no hay ninguno, **el del contenedor** —que ya lo lleva y ve los
mismos datasets montados—. Siempre dice por qué vía va:

```
(duckdb vía: /home/usuario/.venv-curso/bin/python)
...
RESULTADO B2: 16 OK · 0 FALLOS
```

## Cuadernos: uno por SESIÓN de aula

Un cuaderno, un `Ctrl+S`, un entregable:

| Cuaderno | Cubre |
|---|---|
| `notebooks/lab03_completo.ipynb` | LAB03 · métricas de negocio y análisis del log |
| `notebooks/lab04_lab05.ipynb` | LAB04 (jq) + LAB05 (HDFS y Parquet) |
| `notebooks/bitacora_plantilla.ipynb` | Tu bitácora: cópiala como `mi_bitacora.ipynb` |
| `notebooks/lab06_lab07.ipynb` | LAB06 (el ancla LIMPIO-v1) + LAB07 (JOINs y los ausentes) |
| `notebooks/lab08_lab09_lab10.ipynb` | LAB08 (KPIs y auditoría) + LAB09 + LAB10 (Spark y el ETL) |

El manual los nombra sueltos (`lab05.ipynb`, `lab06.ipynb`, `lab09.ipynb`…). **Es un desfase conocido y buscado:** agruparlos evita
reiniciar el kernel entre laboratorios —el ancla y la sesión de Spark viven en él— y reduce las
celdas de entrega de ocho a tres por día.

> ⚠️ **No dejes en `notebooks/` cuadernos sueltos con esos nombres.** Las celdas de archivado
> buscan por patrón (`*lab06*.ipynb`); un cuaderno **vacío** con ese nombre al lado hace que el
> guardián vea «0 celdas con resultados» y **bloquee la entrega**.

**Tu bitácora** es tu copia de `notebooks/bitacora_plantilla.ipynb`, guardada como
`mi_bitacora.ipynb`: es la que recogen las celdas de entrega.

### Un detalle del LAB06 que conviene saber antes de clase

El campo `ciudad` vacío del CSV **DuckDB lo lee como `NULL`, no como cadena vacía**. Escrito
`TRIM(ciudad)=''`, el censo de ciudades vacías devuelve **0 sin dar ningún aviso**. La forma que
usan estos cuadernos y `verificacion_b2.sh` es `COALESCE(TRIM(ciudad),'') = ''` → **3030**, que
caza además los espacios en blanco. **Mismos 16 números, y la regla hace lo que dice que hace.**

## Servicios

| Servicio | Dónde | Para qué |
|---|---|---|
| JupyterLab + PySpark | `IP-DE-LA-VM:8888` (token `curso`) | terminal y cuadernos de todo el curso |
| HDFS didáctico (NameNode) | `IP-DE-LA-VM:9870` | solo la sesión del LAB05 |

## Problemas frecuentes

- **`port is already allocated`** → otro servicio usa el puerto: edita el lado izquierdo del mapeo
  en `docker-compose.yml` (p. ej. `"8889:8888"`) y vuelve a `docker compose up -d`.
- **`permission denied … docker.sock`** (Linux) → `sudo usermod -aG docker $USER` y cerrar sesión.
- **Contenedor `Exited`** → `docker compose logs <servicio>`. Suele ser memoria: puedes apagar el
  HDFS hasta su sesión con `docker compose stop namenode datanode`.
- **Máquina con poca RAM (<4 GB)** → antes de convertir a Parquet:
  `duckdb.sql("SET memory_limit='512MB'")` — más lento, mismos resultados.
- **Apple Silicon / ARM** → todo funciona salvo el HDFS didáctico (imágenes solo AMD64).
- **«Me salen otros números» fuera del contenedor** → host en español: `awk`/`sort` cambian con el
  idioma. Trabaja en la terminal del contenedor; `verificacion.sh` ya fuerza `LC_ALL=C`.
- **`ModuleNotFoundError: No module named 'duckdb'` al pasar `verificacion_b2.sh`** → el
  `pip install duckdb` de la terminal de JupyterLab instala **dentro del contenedor**; el host no
  se entera. Lo arregla `bash aula/prepararb2.sh`, o a mano
  `python3 -m pip install --user --break-system-packages duckdb`. El `--break-system-packages`
  hace falta en Debian 13 y Ubuntu 24: su Python está marcado como *externally managed* (PEP 668)
  y pip se niega a instalar sin permiso explícito.
- **`python3 -m venv` deja un entorno sin `pip`** → falta el paquete `python3-venv`. En Debian el
  `venv` crea la carpeta y el enlace a `bin/python` y **solo después** falla al llegar a
  `ensurepip`, así que parece bueno y no lo es. `sudo apt install -y python3-venv`, borra el
  entorno a medias y repite.
- **Después de un `docker compose down`, el aula vuelve a no encontrar duckdb** → es correcto: lo
  que se instala en un contenedor muere con él. Vuelve a pasar `aula/prepararb2.sh` antes de
  clase. *(Y es, de paso, la lección del Bloque 1 sobre instalaciones efímeras.)*
- **Una tabla de un cuaderno se ve como `| --- | --- |`, o una frase sale partida en dos** → hay
  una línea en blanco entre las filas de la tabla o a mitad de la frase. Markdown exige que esas
  líneas vayan **seguidas**. Lo detecta y lo corrige
  `python3 aula/revisar_markdown_ipynb.py --arreglar notebooks/*.ipynb`; el procedimiento completo
  está en `aula/MARKDOWN.md`.
- **En una tabla se ven etiquetas `<code>&#124;</code>` en vez de una tubería** → la entidad HTML
  no se interpreta dentro de un span de código. En una fila de tabla la tubería se escribe `\|`.
- **Recuperación de desastre** → borra la carpeta, descomprime de nuevo, regenera datasets y `up`.
  Cinco minutos y el curso está intacto.

## Estructura

```
curso-bigdata-ia/
├── README.md                  ← estás aquí
├── docker-compose.yml         ← entorno del alumno (Jupyter + HDFS didáctico)
├── generar_datasets.py        ← la fábrica de datos (semilla 2026)
├── verificacion.sh            ← los 28 números del bloque 1 (docente)
├── verificacion_b2.sh         ← los 16 números del bloque 2 + el ancla LIMPIO-v1
├── datasets/                  ← vacía hasta ejecutar el generador
├── notebooks/                 ← los cuadernos, agrupados por sesión
├── plantillas/                ← ficha de contexto, prompt de rescate, fichas de trabajo
└── aula/                      ← provisión de puestos, publicación e imágenes por USB
    ├── preparar_puesto.sh     ← Debian recién instalado -> git, jq y Docker (sudo)
    ├── prepararb2.sh          ← ritual de apertura del Bloque 2: sincroniza, repara y verifica
    ├── revisar_markdown_ipynb.py  ← audita (y corrige) el Markdown de los cuadernos
    ├── MARKDOWN.md            ← cómo se revisa un cuaderno ya editado
    ├── ACTUALIZAR.md          ← cómo sincroniza el alumnado entre bloques
    └── GITHUB.md              ← cómo publica el docente
```

*Bloques 1–2 · el Bloque 3 añadirá el cuaderno de la API, `aula/n8n-compose.yml` y `servidor-aula/`. Este repositorio se reedita de forma aditiva al inicio de cada bloque.*

## Qué contiene este repositorio (y qué no)

**AQUÍ:** lo necesario para montar las máquinas y trabajar los laboratorios — entorno, datos
(que NACEN en cada máquina), verificación, cuadernos y plantillas.

**EN MOODLE:** toda la teoría — **los manuales del alumno**, diapositivas, chuletas, **la rúbrica
del proyecto** y **la hoja de erratas del Bloque 1**. Nada de eso entra en el repositorio.

**EN NINGÚN SITIO PÚBLICO:** el solucionario del docente y los runbooks de sesión.

## Ciclo entre clases

Apertura de bloque (alumnado y docente): `bash aula/prepararb2.sh` · detalle de la
sincronización: `aula/ACTUALIZAR.md` · publicación del docente: `aula/GITHUB.md` · revisión del
Markdown antes de publicar: `aula/MARKDOWN.md`

Y antes de cada `git push` de material, dos segundos bien invertidos:

```bash
python3 aula/revisar_markdown_ipynb.py notebooks/*.ipynb
```

El ritual de cada bloque es siempre el mismo: **sincronizar, verificar, y solo entonces abrir el
cuaderno**. Si la verificación no da sus números, el problema está en la máquina y no en el
laboratorio — y es mucho más barato descubrirlo a las 16:30 que a las 19:00.
