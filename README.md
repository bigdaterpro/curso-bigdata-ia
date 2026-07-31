# curso-bigdata-ia · Bloque 1

Repositorio ejecutable del curso **Big Data e Inteligencia Artificial Aplicada — Edición Técnica**
(Formación San Miguel · Zaragoza · 40 h). Una descarga = entorno + datos + cuadernos + material.

> Guía completa de cada pieza: `REPO_Manual_del_Zip_Bloque1.pdf` (se distribuye junto a este zip).
> El estudio y los laboratorios viven en `docs/MANUAL_ALUMNO_Bloque1.pdf`: es autosuficiente.

## Puesta en marcha (LAB01)

> ¿Puesto Debian recién instalado? Primero `sudo bash aula/preparar_puesto.sh` (instala
> git, jq y Docker) y cierra/abre sesión. Detalles de aula completa: `aula/` y el vademécum.

```bash
cd curso-bigdata-ia
python3 generar_datasets.py     # ~1-3 min: fabrica los 4 datasets en ./datasets/
docker compose up -d            # la 1ª vez descarga imágenes (minutos); después, segundos
docker compose ps               # jupyter, namenode y datanode deben estar Up
```

Abre **http://localhost:8888** (token: `curso`). En la terminal de JupyterLab:

```bash
ls -lh datasets/
# -rw-r--r-- 60M  ventas.csv      · 1.000.000 ventas
# -rw-r--r-- 4,7M clientes.csv    · 100.000 clientes
# -rw-r--r-- 98K  productos.json  · 480 productos
# -rw-r--r-- 42M  access.log      · 500.000 líneas de servidor web
```

## Los datos: semilla fija 2026

`generar_datasets.py` usa `random.seed(2026)`: **todos los puestos generan datos idénticos**
y tus resultados deben coincidir con los de los manuales. La suciedad de los datasets y el
patrón anómalo del log están plantados a propósito: son parte de los ejercicios. No modifiques
el script (si quieres experimentar, cópialo con otro nombre y otra carpeta de salida).

`verificacion.sh` (uso docente) contrasta los datasets generados con los valores oficiales:
`bash verificacion.sh` → debe terminar en `28 OK · 0 FALLOS`. Requiere `jq`.

## Servicios

| Servicio | Dónde | Para qué |
|---|---|---|
| JupyterLab + PySpark | `localhost:8888` (token `curso`) | terminal y cuadernos de todo el curso |
| HDFS didáctico (NameNode) | `localhost:9870` | solo sesión 3 (LAB05) |
| IA del aula (Open WebUI) | `http://IP-del-aula:8080` | la monta el docente con `servidor-aula/` |

El cuaderno del LAB05 usa DuckDB. Si el contenedor no lo trae, en una terminal de JupyterLab:
`pip install duckdb`.

## Problemas frecuentes

- **`port is already allocated`** → otro servicio usa el puerto: edita el lado izquierdo del
  mapeo en `docker-compose.yml` (p. ej. `"8889:8888"`) y vuelve a `docker compose up -d`.
- **`permission denied … docker.sock`** (Linux) → `sudo usermod -aG docker $USER` y cerrar sesión.
- **Contenedor `Exited`** → `docker compose logs <servicio>` y lee la última pantalla. En WSL2
  suele ser memoria: puedes apagar el HDFS hasta la sesión 3 con
  `docker compose stop namenode datanode`.
- **`pip` sin red dentro del contenedor** (el host sí resuelve) → contenedor nacido en otra
  red: mira `docker exec jupyter cat /etc/resolv.conf`; si dice "NO EXTERNAL NAMESERVERS",
  añade `{"dns": ["10.0.2.3", "1.1.1.1"]}` a `/etc/docker/daemon.json`, reinicia docker y
  `docker compose up -d --force-recreate`.
- **Máquina con poca RAM (<4 GB)** → antes de convertir en el lab05:
  `duckdb.sql("SET memory_limit='512MB'")` — más lento, mismos resultados.
- **Apple Silicon / ARM** → todo funciona salvo el HDFS didáctico (imágenes solo AMD64):
  esa demo requiere un puesto x86.
- **«Me salen otros números» fuera del contenedor** → host en español: `awk`/`sort` cambian
  con el idioma (coma decimal, cotejo). Trabaja en la terminal del contenedor;
  `verificacion.sh` ya fuerza `LC_ALL=C`.
- **Recuperación de desastre** → borra la carpeta, descomprime de nuevo, regenera datasets y
  `up`. Cinco minutos y el curso está intacto.

## Estructura

```
curso-bigdata-ia/
├── README.md                  ← estás aquí
├── docker-compose.yml         ← entorno del alumno (Jupyter + HDFS didáctico)
├── generar_datasets.py        ← la fábrica de datos (semilla 2026)
├── verificacion.sh            ← batería de comprobación de los datos (docente)
├── datasets/                  ← vacía hasta ejecutar el generador
├── notebooks/lab03_completo.ipynb   ← métricas, log y gráficas (sesión 2)
├── notebooks/lab04_lab05.ipynb      ← jq, HDFS y Parquet (sesión 3)
├── plantillas/                ← activos del taller: ficha de contexto, prompt
│                                 de rescate, ficha de exploración, tabla LAB05
├── aula/                      ← provisión de puestos: preparar_puesto.sh + imágenes por USB
```

*Bloque 1 · El Bloque 2 añadirá los cuadernos lab06–lab10 (DuckDB y PySpark). Este repositorio se reedita de forma aditiva al inicio de cada bloque.*

## Qué contiene este repositorio (y qué no)
AQUÍ: lo necesario para montar las máquinas y trabajar los labs — entorno (docker-compose.yml,
aula/, servidor-aula/), datos (generar_datasets.py: los datasets NACEN en cada máquina),
verificación (verificacion.sh), cuadernos (notebooks/lab*.ipynb) y plantillas de trabajo (plantillas/).
EN MOODLE: toda la teoría — manuales, diapositivas, chuletas y la rúbrica del proyecto.

## Puesta en marcha en una máquina
    python3 generar_datasets.py && bash verificacion.sh     # 28 OK 
    docker compose up -d                                     # Jupyter en :8888
Ciclo entre clases: aula/ACTUALIZAR.md · Publicación del docente: aula/GITHUB.md
