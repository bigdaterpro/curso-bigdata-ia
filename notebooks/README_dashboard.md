# EL CUADRO DE MANDO · guía de despliegue
## Tres rutas, una decisión que hay que tomar la noche anterior

> **Qué es:** una aplicación web que lee **el Parquet que escribió su Spark**, lo consulta con
> **DuckDB**, lo dibuja con **Plotly**, y tiene un botón que pide a **Gemini** un informe ejecutivo
> a partir de KPIs **ya verificados**. Filtros por canal y por periodo, control del ancla en la
> cabecera, y el prompt exacto a la vista.

```
   tu Parquet  ->  DuckDB  ->  Plotly  ->  navegador
                      |
                      +->  KPIs verificados  ->  Gemini  ->  informe  ->  TU auditoria
```

---

# ⚠️ LA DECISIÓN · tómala el jueves por la noche, no el viernes a las siete

Las tres rutas cubren el mismo contenido del programa oficial —*visualizaciones interactivas y
dashboards*—. Cambian el riesgo y el tiempo de aula.

| | Qué es | Riesgo | Min de aula |
|---|---|---|---|
| **A · dentro de Jupyter** | `pip install` + `streamlit run` en la terminal que ya usan | **Medio**: hay que publicar el puerto 8501 | 45 |
| **B · contenedor aparte** | `docker compose -f aula/dashboard-compose.yml up -d` | **Medio-alto**: 15 × pip dentro del contenedor | 50 |
| **C · en el cuaderno** | Plotly inline, sin servidor | **Cero** | 30 |

**Prueba la A esta noche. Si el puerto no se deja publicar sin romper nada, ve a la B. Si la red del
aula va justa, ve a la C sin remordimiento** — Plotly en el cuaderno **también es interactivo**
(zoom, *hover*, series que se encienden y apagan) y cubre el contenido igual.

> 💡 **Sea cual sea la ruta, el paso previo es el mismo:** que su `datasets/salida/` tenga el
> Parquet. Lo demás es fontanería.

---

# RUTA A · dentro del contenedor de Jupyter *(recomendada)*

**① Publicar el puerto.** En el `docker-compose.yml` principal, en el servicio de Jupyter:

```yaml
    ports:
      - "8888:8888"
      - "8501:8501"      # <-- el cuadro de mando
```

```bash
# ⌂ HOST
docker compose up -d          # recrea el contenedor con el puerto nuevo
```

> ⚠️ **Esto recrea el contenedor.** Los cuadernos viven en un volumen y no se pierden, **pero
> pruébalo tú antes** con un puesto de verdad. Y hazlo **el jueves**, no el viernes.

**② Instalar y arrancar.** En la ▸ **Terminal de Jupyter**:

```bash
pip install streamlit plotly
cd ~/work/notebooks          # o donde viva app.py
export GEMINI_API_KEY=tu_clave
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

**③ Abrir:** `http://IP-DE-LA-VM:8501`

> ⚠️ **La IP de la VM, no `localhost`.** El `localhost` del alumno es su Windows. Es la misma
> corrección que ya conocen de `:8888` y `:9870`.

> 💡 La terminal se queda ocupada mientras la app corre. **Es lo normal**: es un servidor. Se para
> con `Ctrl+C`.

---

# RUTA B · contenedor aparte

**① Colocar los ficheros:**
```
   aula/dashboard-compose.yml
   notebooks/app.py
```

**② Levantar:**
```bash
# ⌂ HOST
export GEMINI_API_KEY=tu_clave          # se hereda; NO se escribe en el compose
docker compose -f aula/dashboard-compose.yml up -d
docker compose -f aula/dashboard-compose.yml logs -f    # espera a "You can now view"
```

**③ Abrir:** `http://IP-DE-LA-VM:8501`

**Lo que enseña este compose, y conviene señalarlo en voz alta:**

| Detalle | La lección |
|---|---|
| `../notebooks` y `../datasets` | **Docker resuelve las rutas relativas contra la carpeta del compose.** La misma trampa del n8n |
| `../datasets:/datasets:ro` | **Solo lectura.** La primera ley del curso, hasta el último día |
| `GEMINI_API_KEY=${GEMINI_API_KEY:-}` | **La clave se hereda del entorno, no se escribe en el fichero.** El fichero se sube a un repositorio; la clave no |
| `restart: unless-stopped` | Sobrevive al reinicio, como el servidor de IA |

> ⚠️ **El coste real:** el primer arranque instala los paquetes dentro del contenedor. **Quince
> puestos a la vez son varios cientos de megas por la red del aula.** Si la red va justa, ruta C.

---

# RUTA C · en el cuaderno *(plan B sin riesgo, y sigue siendo interactivo)*

Ni servidor ni puertos. En el `lab17_cierre_integral.ipynb`, la sección del cuadro de mando dibuja
con Plotly directamente en el cuaderno:

```python
import plotly.express as px
px.bar(df_ciudad, x="millones", y="ciudad", orientation="h").show()
```

**Sigue siendo interactivo:** zoom, *hover* con los valores, leyenda que enciende y apaga series. Y
se exporta dentro del HTML del entregable.

**Lo que se pierde:** los filtros de la barra lateral y el botón del informe. El informe se genera
igual desde la celda de la API, que ya está en el cuaderno.

---

# LA CLAVE DE API · dónde vive en cada ruta

| Ruta | Dónde |
|---|---|
| A | `export GEMINI_API_KEY=…` en la terminal, **antes** de `streamlit run` |
| B | `export …` en el host, **antes** de `docker compose up`. El compose la hereda |
| C | `export …` en la terminal + **reiniciar el kernel** |

**En ninguna se escribe dentro de un fichero.** Es la tercera vez que aparece la liturgia en el
curso: entorno, credencial referenciada, y ahora variable heredada por el contenedor. **Ya es un
hábito, no una norma.**

---

# QUÉ SE VE EN LA APP · y qué preguntar sobre cada cosa

| Zona | Qué preguntar en clase |
|---|---|
| **Banda del ancla** | *«¿Qué pasa si esa banda sale roja? ¿Se puede seguir mirando el resto?»* |
| **Los cuatro KPIs** | *«Quitad un canal en el filtro. ¿Qué número cambia y cuál no? ¿Por qué el ticket apenas se mueve?»* |
| **Casilla «solo con ciudad conocida»** | *«Marcadla. Se han ido 3.030 ventas. **¿Eso es limpiar o es esconder?**»* |
| **Mes pico** | *«Diciembre. ¿Es campaña, es estacionalidad, o es un artefacto de los datos?»* |
| **Ver los datos en crudo** | *«Todo gráfico debe poder abrirse. Un gráfico que no enseña su tabla es una opinión»* |
| **Botón del informe** | *«¿Cita solo las cifras que le dimos? ¿Ha redondeado raro? ¿Ha inventado alguna?»* |
| **Ver el prompt exacto** | *«Las cinco piezas están ahí dentro. Buscadlas: rol, contexto, tarea, formato… y la regla»* |

---

# AVERÍAS

| Síntoma | Qué es | Arreglo |
|---|---|---|
| La página no carga | Estás entrando por `localhost` | **La IP de la VM** |
| `NO CUADRA · N filas` | No hay Parquet o está incompleto | La app cae al CSV sola; reejecuta el LAB10 luego |
| El sidebar dice «el CSV crudo (plan B)» | Falta el Parquet | Igual funciona. Anótalo |
| «Sin clave» en el informe | La app arrancó antes del `export` | `export …` y **volver a arrancar la app** |
| `HTTP 429` al generar | **Cuota, no avería** | Esperar un minuto |
| `HTTP 404` al generar | El nombre del modelo caducó | `export GEMINI_MODELO=…` y rearrancar |
| El `pip install` del contenedor se eterniza | Red del aula, 15 a la vez | **Ruta C.** Y dilo sin dramatismo |
| La terminal queda «colgada» | Es un servidor corriendo | Normal. `Ctrl+C` para parar |

---

*Guía del cuadro de mando · Formación San Miguel · Zaragoza*
