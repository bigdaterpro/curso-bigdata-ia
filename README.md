# curso-bigdata-ia

Repositorio ejecutable del curso **Big Data e Inteligencia Artificial Aplicada — Edición Técnica**
(Formación San Miguel · Zaragoza · 40 h). Una descarga = entorno + datos + cuadernos + material.

**Estado: completo — Bloques 1, 2 y 3 (Cierre).**

> El estudio y los laboratorios viven en los manuales de Moodle: son autosuficientes.
> Este repositorio es lo que se **ejecuta**.

---

## Puesta en marcha

> ¿Puesto Debian recién instalado? Primero `sudo bash aula/preparar_puesto.sh` (instala git, jq y
> Docker) y cierra/abre sesión.

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

### Antes del Bloque 2

```bash
bash aula/prepararb2.sh         # deja el host listo para SQL, JOINs y Spark
```

---

## Los datos: semilla fija 2026

`generar_datasets.py` usa `random.seed(2026)`: **todos los puestos generan datos idénticos** y tus
resultados deben coincidir con los de los manuales. La suciedad de los datasets y el patrón anómalo
del log están plantados a propósito: son parte de los ejercicios. No modifiques el script (si
quieres experimentar, cópialo con otro nombre y otra carpeta de salida).

### Verificación

| Script | Qué contrasta | Debe dar |
|---|---|---|
| `verificacion.sh` | Los datos del **Bloque 1**, con herramientas de shell | `28 OK · 0 FALLOS` |
| `verificacion_b2.sh` | Los números del **Bloque 2**, con DuckDB | `16 OK · 0 FALLOS` |

`verificacion.sh` requiere `jq`. `verificacion_b2.sh` busca solo un intérprete que tenga DuckDB: el
del `PATH`, el de `~/.venv-curso` o el del contenedor.

> La vista `ventas_limpio` de `verificacion_b2.sh` **es la definición canónica LIMPIO-v1 del
> curso**: tres reglas escritas, y el ancla que las gobierna.

### Las cifras que gobiernan todo el curso

| | |
|---|---|
| Filas limpias | **999.535** (de 1.000.000: se van 465 con precio imposible) |
| Facturación | **429.892.547,06 €** · ticket medio **430,09 €** |
| Clientes activos | **99.996** de 100.000 — **cuatro no han comprado nunca** |
| Ventas sin ciudad | **3.030**, que se conservan a propósito |
| CSV → Parquet | 61.942.187 → 17.178.881 bytes = **3,61×** |

Si un número no coincide, no sigas: algo cambió y merece la pena saber qué.

---

## Servicios

| Servicio | Dónde | Para qué |
|---|---|---|
| JupyterLab + PySpark | `localhost:8888` (token `curso`) | terminal y cuadernos de todo el curso |
| HDFS didáctico (NameNode) | `localhost:9870` | solo sesión 3 (LAB05) |
| Cuadro de mando (Streamlit) | `IP-de-la-VM:8501` | sesión 10 (LAB17) |
| Servidor local de IA (Ollama) | `IP-del-servidor:11434` | bloque extra, lo monta el docente |

### Publicar el puerto del cuadro de mando

```bash
bash aula/publicar_puerto.sh    # escribe un override sin tocar tu compose
```

> ⚠️ **La IP de la VM, no `localhost`.** Tercera vez en el curso: `:8888`, `:9870`, `:8501`.

---

## Los cuadernos

| Cuaderno | Bloque | Qué se hace |
|---|---|---|
| `lab03_completo.ipynb` | 1 | Métricas con shell, logs y caracterización del bot |
| `lab04_lab05.ipynb` | 1 | `jq` sobre el catálogo · CSV contra Parquet |
| `lab06_lab07.ipynb` | 2 | SQL con DuckDB · LIMPIO-v1 · JOINs y los cuatro ausentes |
| `lab08_lab09_lab10.ipynb` | 2 | KPIs publicados · **auditoría a la IA** · Spark · el Parquet maestro |
| `lab11_lab12_lab14.ipynb` | 3 | Prompting · salidas estructuradas · la API desde Python |
| `lab17_comercial_aragonesa.ipynb` | 3 | **El cierre integral**: pipeline completo con cuadro de mando |
| `reto_lab08_solucion.ipynb` | 2 | Solución comentada del reto de los tres conjuntos |
| `cliente_ia_local.ipynb` | extra | Llamar al servidor local de IA desde el cuaderno |
| `bitacora_plantilla.ipynb` | — | La bitácora de cada sesión |
| `proyecto_plantilla.ipynb` | — | El proyecto de continuidad |

### El LAB17 y sus variantes

El cierre puede montarse de tres formas. **Se reparte solo una**: si un puesto tiene varias, la
celda de archivado encuentra varios `*lab17*.ipynb` y la entrega se lía.

| | Cuaderno | Cuándo |
|---|---|---|
| **Principal** | `lab17_comercial_aragonesa.ipynb` | La app corre en el propio Jupyter |
| Alternativa | `alternativas/lab17_contenedor.ipynb` | La app en su propio contenedor |
| Alternativa | `alternativas/lab17_sin_servidor.ipynb` | Sin servidor: Plotly dentro del cuaderno |

Levantar la aplicación:

```bash
pip install streamlit plotly "starlette<1.4"
export GEMINI_API_KEY=tu_clave
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

> ⚠️ **El pin `"starlette<1.4"` es obligatorio.** La versión 1.4 añadió un argumento que Streamlit
> no le pasa: el servidor arranca y **el navegador recibe un 500** en cuanto pide compresión. Si lo
> quitas, vuelve el fallo.

---

## Los prompts de informe

En `notebooks/prompts/`. Sirven para que la IA redacte el informe del cuadro de mando **con cifras
verificadas**, y para auditarlo después.

| Fichero | Para qué |
|---|---|
| `PROMPT_A_informe_texto.md` | Informe con gráficos de texto y tablas |
| `PROMPT_B_informe_mermaid.md` | Informe con diagramas Mermaid y tablas |
| `CONTEXTO_INFORME_*.md` | Para que tu asistente te ayude a adaptarlos |

**Los dos son universales: no llevan ni una cifra dentro.** Detectan solos si hay filtros aplicados
comparando el total contra el ancla del curso, y obligan a declararlo **en el título del informe**.

---

## Herramientas del docente

| Fichero | Qué hace |
|---|---|
| `aula/preparar_puesto.sh` | Provisiona un puesto desde cero |
| `aula/prepararb2.sh` | Deja el host listo para el Bloque 2 |
| `aula/publicar_puerto.sh` | Publica el 8501 sin tocar el compose original |
| `aula/pulir_cuadernos.py` | Repara defectos de formato en los `.ipynb` |
| `aula/verificar_cuadernos.py` | 16 pruebas independientes sobre los cuadernos |
| `aula/dashboard-compose.yml` | Solo para la variante en contenedor |
| `aula/docker-compose.override.yml` | Lo que escribe `publicar_puerto.sh` |
| `aula/ACTUALIZAR.md` | El ciclo entre clases |
| `aula/GITHUB.md` | La publicación del docente |

```bash
python3 aula/verificar_cuadernos.py notebooks/*.ipynb          # el juez
python3 aula/pulir_cuadernos.py --arreglar --imports --copia notebooks/*.ipynb
```

> **El verificador no comparte código con el reparador, y es deliberado:** si compartieran
> funciones, compartirían los puntos ciegos.

---

## Problemas frecuentes

- **`port is already allocated`** → otro servicio usa el puerto: edita el lado izquierdo del mapeo
  en `docker-compose.yml` (p. ej. `"8889:8888"`) y vuelve a `docker compose up -d`.
- **`permission denied … docker.sock`** (Linux) → `sudo usermod -aG docker $USER` y cerrar sesión.
- **Contenedor `Exited`** → `docker compose logs <servicio>` y lee la última pantalla. En WSL2 suele
  ser memoria: puedes apagar el HDFS hasta la sesión 3 con `docker compose stop namenode datanode`.
- **`pip` sin red dentro del contenedor** (el host sí resuelve) → contenedor nacido en otra red:
  mira `docker exec jupyter cat /etc/resolv.conf`; si dice «NO EXTERNAL NAMESERVERS», añade
  `{"dns": ["10.0.2.3", "1.1.1.1"]}` a `/etc/docker/daemon.json`, reinicia docker y
  `docker compose up -d --force-recreate`.
- **Máquina con poca RAM (<4 GB)** → antes de convertir en el LAB05:
  `duckdb.sql("SET memory_limit='512MB'")` — más lento, mismos resultados.
- **Apple Silicon / ARM** → todo funciona salvo el HDFS didáctico (imágenes solo AMD64): esa demo
  requiere un puesto x86.
- **«Me salen otros números» fuera del contenedor** → host en español: `awk`/`sort` cambian con el
  idioma (coma decimal, cotejo). Trabaja en la terminal del contenedor; `verificacion.sh` ya fuerza
  `LC_ALL=C`.
- **El cuadro de mando da 500 en el navegador** pero `/_stcore/health` responde → es `starlette`
  1.4. `pip install "starlette<1.4"`.
- **DuckDB no lee el Parquet que escribió Spark** → Spark escribe una **carpeta**: hace falta el
  comodín `.../ventas_limpio.parquet/*.parquet`.
- **El HTML de la entrega sale vacío** → no se guardó antes de archivar. `Ctrl+S` y repetir. Se
  detecta contando los `[n]:`, no por el tamaño del fichero.
- **Recuperación de desastre** → borra la carpeta, clona de nuevo, regenera datasets y `up`. Cinco
  minutos y el curso está intacto.

---

## Estructura

```
curso-bigdata-ia/
├── README.md                     ← estás aquí
├── docker-compose.yml            ← entorno del alumno (Jupyter + HDFS didáctico)
├── generar_datasets.py           ← la fábrica de datos (semilla 2026)
├── verificacion.sh               ← comprobación de los datos del Bloque 1 (28 OK)
├── verificacion_b2.sh            ← comprobación de los números del Bloque 2 (16 OK)
├── datasets/                     ← vacía hasta ejecutar el generador
├── notebooks/
│   ├── lab03_completo.ipynb          Bloque 1
│   ├── lab04_lab05.ipynb             Bloque 1
│   ├── lab06_lab07.ipynb             Bloque 2
│   ├── lab08_lab09_lab10.ipynb       Bloque 2
│   ├── lab11_lab12_lab14.ipynb       Bloque 3
│   ├── lab17_comercial_aragonesa.ipynb   Bloque 3 · el cierre
│   ├── alternativas/                 las otras dos formas de montar el LAB17
│   ├── app.py                        el cuadro de mando (Streamlit + DuckDB)
│   ├── prompts/                      los prompts de informe y sus contextos
│   ├── MEJORAS.md                    las tres mejoras del LAB17
│   ├── README_dashboard.md           las tres formas de levantar la app
│   ├── reto_lab08_solucion.ipynb     solución del reto de los tres conjuntos
│   ├── cliente_ia_local.ipynb        cliente del servidor local de IA
│   ├── bitacora_plantilla.ipynb      la bitácora de cada sesión
│   └── proyecto_plantilla.ipynb      el proyecto de continuidad
├── plantillas/                   ← activos del taller: ficha de contexto, prompt de
│                                    rescate, ficha de exploración, tabla LAB05,
│                                    prompt de auditoría de SQL
└── aula/                         ← provisión de puestos y herramientas del docente
```

---

## Qué contiene este repositorio (y qué no)

**AQUÍ:** lo necesario para montar las máquinas y trabajar los labs — entorno
(`docker-compose.yml`, `aula/`), datos (`generar_datasets.py`: los datasets **nacen** en cada
máquina), verificación (`verificacion.sh`, `verificacion_b2.sh`), cuadernos
(`notebooks/lab*.ipynb`), la aplicación (`app.py`) y las plantillas de trabajo.

**EN MOODLE:** toda la teoría — manuales, diapositivas, chuletas, rúbricas y el material del bloque
extra.

---

## El hilo del curso, en una línea

Del `wc -l` en una terminal a un cuadro de mando que lee **tu** Parquet, redacta un informe con IA y
**lo audita contra tu propio número**. Todo lo demás son herramientas.

---

*Curso completo · Bloques 1, 2 y 3 · Formación San Miguel · Zaragoza*
