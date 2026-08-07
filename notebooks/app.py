"""
CUADRO DE MANDO · Comercial Aragonesa S.L.  ·  v2
Curso Big Data e IA Aplicada · Formación San Miguel · Zaragoza

Todo lo del curso, con cara: tu Parquet limpio, los JOINs con clientes y
productos, los filtros, y la IA como componente auditado.

    streamlit run app.py --server.port 8501 --server.address 0.0.0.0

CÓMO ESTÁ ORGANIZADO  (léelo antes de tocar nada: son cinco secciones)

    1 · DATOS      las vistas y el ancla. Todo sale de aquí
    2 · FILTROS    la barra lateral. Devuelve UNA cláusula WHERE
    3 · PÁGINAS    una función por pestaña. Se añaden aquí
    4 · IA         el prompt editable y su auditoría
    5 · ARRANQUE   qué pestaña se dibuja

Para AÑADIR UNA PESTAÑA: escribe una función `pagina_loquesea(con, filtro)`
y añádela al diccionario PAGINAS del final. Nada más.
"""
import json
import os
import time
import urllib.error
import urllib.request

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

# ── ANCLAS DEL CURSO · el juez de todo lo que se dibuja ─────────────────────
ANCLA_FILAS = 999_535
ANCLA_FACTURACION = 429_892_547.06
ANCLA_TICKET = 430.09
ANCLA_CIUDADES = 10

SALIDA = "../datasets/salida"
PARQUET = f"{SALIDA}/ventas_limpio.parquet/*.parquet"
CSV_VENTAS = "../datasets/ventas.csv"
CSV_CLIENTES = "../datasets/clientes.csv"
JSON_PRODUCTOS = "../datasets/productos.json"

# Los KPIs que publicaste con COPY en el LAB08. La app NO los usa para dibujar
# —recalcula en vivo, porque los filtros lo exigen— pero SÍ los usa como JUEZ:
# el CSV y la consulta en vivo vienen por caminos distintos y deben coincidir.
KPIS = {"kpi_canal.csv": "canal", "kpi_ciudad.csv": "ciudad", "kpi_mes.csv": "mes"}

st.set_page_config(page_title="Comercial Aragonesa · cuadro de mando",
                   page_icon="📊", layout="wide")


def es(x, dec=2):
    """Notación española: punto para los miles, coma para los decimales."""
    return (f"{x:,.{dec}f}".replace(",", "\x00").replace(".", ",").replace("\x00", "."))


# ═══════════════════════════════════════════════════════════════════════════
# 1 · DATOS
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_resource
def conectar():
    """Tres vistas: ventas_limpio (tu almacén), clientes y productos.

    ventas_limpio sale del Parquet que escribió tu Spark. Si no está, se
    reconstruye LIMPIO-v1 sobre el CSV: mismos números, otro camino.
    """
    con = duckdb.connect()
    try:
        con.sql(f"CREATE OR REPLACE VIEW ventas_limpio AS SELECT * FROM '{PARQUET}'")
        con.sql("SELECT COUNT(*) FROM ventas_limpio").fetchone()
        origen = "el Parquet maestro (tu LAB10)"
    except Exception:
        con.sql(f"""CREATE OR REPLACE VIEW ventas_limpio AS
            SELECT id_venta, fecha, id_cliente, id_producto, categoria,
                   unidades, precio_unitario,
                   CASE WHEN COALESCE(TRIM(ciudad), '') = '' THEN NULL
                        ELSE UPPER(SUBSTR(TRIM(ciudad),1,1))
                             || LOWER(SUBSTR(TRIM(ciudad),2)) END AS ciudad,
                   canal
            FROM '{CSV_VENTAS}'
            WHERE precio_unitario > 0""")
        origen = "el CSV crudo (plan B — revisa tu LAB10)"

    # Clientes y productos: si existe su Parquet, se usa; si no, el original.
    # Es el reto del cierre, y la app lo nota sola.
    if os.path.exists(f"{SALIDA}/clientes.parquet"):
        con.sql("CREATE OR REPLACE VIEW clientes AS "
                f"SELECT * FROM '{SALIDA}/clientes.parquet'")
        fmt_clientes = "Parquet"
    else:
        con.sql(f"CREATE OR REPLACE VIEW clientes AS SELECT * FROM '{CSV_CLIENTES}'")
        fmt_clientes = "CSV"

    if os.path.exists(f"{SALIDA}/productos.parquet"):
        con.sql("CREATE OR REPLACE VIEW productos AS "
                f"SELECT * FROM '{SALIDA}/productos.parquet'")
        fmt_productos = "Parquet"
    else:
        con.sql(f"""CREATE OR REPLACE VIEW productos AS
            SELECT id, nombre, categoria, precio,
                   stock.central + stock.tiendas AS stock_total
            FROM read_json('{JSON_PRODUCTOS}')""")
        fmt_productos = "JSON"

    return con, origen, fmt_clientes, fmt_productos


con, origen, FMT_CLIENTES, FMT_PRODUCTOS = conectar()


def q(sql):
    return con.sql(sql).df()


def uno(sql):
    return con.sql(sql).fetchone()[0]


# ═══════════════════════════════════════════════════════════════════════════
# 2 · FILTROS · la barra lateral devuelve UNA cláusula WHERE
# ═══════════════════════════════════════════════════════════════════════════
def barra_lateral():
    st.sidebar.title("Filtros")
    st.sidebar.caption(f"Ventas: {origen}")
    st.sidebar.caption(f"Clientes: {FMT_CLIENTES} · Productos: {FMT_PRODUCTOS}")

    canales = [c[0] for c in con.sql(
        "SELECT DISTINCT canal FROM ventas_limpio ORDER BY canal").fetchall()]
    sel_canal = st.sidebar.multiselect("Canal", canales, default=canales)

    cats = [c[0] for c in con.sql(
        "SELECT DISTINCT categoria FROM ventas_limpio ORDER BY categoria").fetchall()]
    sel_cat = st.sidebar.multiselect("Categoría", cats, default=cats)

    ciudades = [c[0] for c in con.sql(
        "SELECT DISTINCT ciudad FROM ventas_limpio WHERE ciudad IS NOT NULL "
        "ORDER BY ciudad").fetchall()]
    sel_ciudad = st.sidebar.multiselect("Ciudad", ciudades, default=[])

    meses = [m[0] for m in con.sql(
        "SELECT DISTINCT STRFTIME(fecha,'%Y-%m') AS m FROM ventas_limpio "
        "ORDER BY m").fetchall()]
    desde, hasta = st.sidebar.select_slider(
        "Periodo", options=meses, value=(meses[0], meses[-1]))

    tope = float(uno("SELECT MAX(unidades*precio_unitario) FROM ventas_limpio"))
    min_imp = st.sidebar.number_input("Importe mínimo de la venta (€)",
                                      0.0, tope, 0.0, step=50.0)

    solo_ciudad = st.sidebar.checkbox(
        "Solo ventas con ciudad conocida", value=False,
        help="Las ventas sin ciudad son 3.030. Activarlo es una DECISIÓN: "
             "declárala en tu informe.")

    # El filtro se escribe con «{v}» delante de cada columna. En una consulta
    # sencilla se sustituye por nada; dentro de un JOIN, por el alias de ventas.
    # Sin esto, «categoria» es ambigua en cuanto se une con productos.
    t = [f"STRFTIME({{v}}fecha,'%Y-%m') BETWEEN '{desde}' AND '{hasta}'"]
    t.append("{v}canal IN (" + ",".join(repr(c) for c in sel_canal) + ")"
             if sel_canal else "1=0")
    t.append("{v}categoria IN (" + ",".join(repr(c) for c in sel_cat) + ")"
             if sel_cat else "1=0")
    if sel_ciudad:
        t.append("{v}ciudad IN (" + ",".join(repr(c) for c in sel_ciudad) + ")")
    if min_imp > 0:
        t.append(f"{{v}}unidades*{{v}}precio_unitario >= {min_imp}")
    if solo_ciudad:
        t.append("{v}ciudad IS NOT NULL")
    completo = " AND ".join(t)
    st.session_state.setdefault("filtro_inicial", completo)
    return completo


def donde_sin_filtros():
    """El filtro tal y como queda cuando no se ha tocado nada en la barra."""
    return st.session_state.get("filtro_inicial", "")


def donde(filtro, alias=""):
    """Pone el alias en el filtro: donde(f) para una tabla, donde(f,'v') en JOIN."""
    return filtro.format(v=(alias + "." if alias else ""))


def banda_del_ancla():
    total = uno("SELECT COUNT(*) FROM ventas_limpio")
    if total == ANCLA_FILAS:
        st.success(f"ANCLA VERIFICADA · {es(total, 0)} filas en el almacén")
    else:
        st.error(f"NO CUADRA · {es(total, 0)} filas, se esperaban "
                 f"{es(ANCLA_FILAS, 0)}. Averigua por qué antes de mirar nada más.")


# ═══════════════════════════════════════════════════════════════════════════
# 3 · PÁGINAS · una función por pestaña
# ═══════════════════════════════════════════════════════════════════════════
def pagina_resumen(filtro):
    k = q(f"""SELECT COUNT(*) AS filas,
                     SUM(unidades*precio_unitario) AS facturacion,
                     SUM(unidades*precio_unitario)/COUNT(*) AS ticket,
                     COUNT(DISTINCT ciudad) AS ciudades,
                     COUNT(DISTINCT id_cliente) AS clientes
              FROM ventas_limpio WHERE {donde(filtro)}""").iloc[0]
    if int(k.filas) == 0:
        st.warning("El filtro no deja pasar ninguna venta.")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Facturación", f"{es(k.facturacion/1e6, 1)} M€")
    c2.metric("Operaciones", es(int(k.filas), 0))
    c3.metric("Ticket medio", f"{es(k.ticket)} €")
    c4.metric("Clientes activos", es(int(k.clientes), 0))
    st.caption(f"Sin filtros deben salir los canónicos: {es(ANCLA_FACTURACION)} € "
               f"y ticket {es(ANCLA_TICKET)}.")

    izq, der = st.columns(2)
    with izq:
        st.subheader("Por canal")
        d = q(f"""SELECT canal, ROUND(SUM(unidades*precio_unitario)/1e6,1) AS millones
                  FROM ventas_limpio WHERE {donde(filtro)}
                  GROUP BY canal ORDER BY millones DESC""")
        st.plotly_chart(px.bar(d, x="canal", y="millones", text="millones"),
                        width="stretch")
    with der:
        st.subheader("Por ciudad")
        d = q(f"""SELECT ciudad, ROUND(SUM(unidades*precio_unitario)/1e6,1) AS millones
                  FROM ventas_limpio WHERE {donde(filtro)} AND ciudad IS NOT NULL
                  GROUP BY ciudad ORDER BY millones DESC""")
        st.plotly_chart(px.bar(d, x="millones", y="ciudad", orientation="h")
                        .update_yaxes(autorange="reversed"), width="stretch")

    st.subheader("Evolución mensual")
    d = q(f"""SELECT STRFTIME(fecha,'%Y-%m') AS mes,
                     ROUND(SUM(unidades*precio_unitario)/1e6,2) AS millones,
                     COUNT(*) AS operaciones
              FROM ventas_limpio WHERE {donde(filtro)} GROUP BY mes ORDER BY mes""")
    st.plotly_chart(px.line(d, x="mes", y="millones", markers=True), width="stretch")
    if not d.empty:
        pico = d.loc[d.millones.idxmax()]
        st.info(f"Mes pico: **{pico.mes}** con **{es(pico.millones)} M€** y "
                f"{es(int(pico.operaciones), 0)} operaciones.")
    with st.expander("Ver los datos en crudo"):
        st.dataframe(d, width="stretch")


def pagina_ventas(filtro):
    n = uno(f"SELECT COUNT(*) FROM ventas_limpio WHERE {donde(filtro)}")
    st.subheader(f"{es(n, 0)} ventas pasan el filtro")
    st.caption("La tabla enseña las 500 primeras. El recuento es sobre todas.")
    st.dataframe(q(f"""SELECT id_venta, fecha, id_cliente, id_producto, categoria,
                              unidades, precio_unitario,
                              ROUND(unidades*precio_unitario, 2) AS importe,
                              ciudad, canal
                       FROM ventas_limpio WHERE {donde(filtro)}
                       ORDER BY importe DESC LIMIT 500"""), width="stretch")

    st.subheader("Reparto por categoría")
    d = q(f"""SELECT categoria,
                     ROUND(SUM(unidades*precio_unitario)/1e6,2) AS millones,
                     COUNT(*) AS operaciones
              FROM ventas_limpio WHERE {donde(filtro)}
              GROUP BY categoria ORDER BY millones DESC""")
    st.plotly_chart(px.bar(d, x="categoria", y="millones", text="millones"),
                    width="stretch")


def pagina_clientes(filtro):
    st.subheader("Los tres segmentos")
    seg = q(f"""SELECT c.segmento,
                       COUNT(DISTINCT c.id_cliente) AS clientes,
                       COUNT(v.id_venta)            AS operaciones,
                       ROUND(SUM(v.unidades*v.precio_unitario)/1e6, 1) AS millones
                FROM clientes c
                LEFT JOIN ventas_limpio v ON v.id_cliente = c.id_cliente
                                          AND ({donde(filtro, 'v')})
                GROUP BY c.segmento ORDER BY millones DESC""")
    st.dataframe(seg, width="stretch")
    suma = int(seg.operaciones.sum())
    st.caption(f"Control del oficio: las operaciones de los tres segmentos suman "
               f"**{es(suma, 0)}**. Sin filtros, tienen que dar las filas de tu vista.")

    st.divider()
    st.subheader("Ficha de cliente")
    st.caption("Es el JOIN del LAB07, con cara: un cliente y todo lo que compró.")

    izq, der = st.columns([1, 2])
    with izq:
        modo = st.radio("Buscar por", ["Id", "Apellido"], horizontal=True)
        if modo == "Id":
            ident = st.number_input("id_cliente", 1,
                                    int(uno("SELECT MAX(id_cliente) FROM clientes")),
                                    1, step=1)
            elegido = int(ident)
        else:
            ape = st.text_input("Apellido (o parte)", "")
            cand = q(f"""SELECT id_cliente, nombre, apellido, ciudad, segmento
                         FROM clientes
                         WHERE lower(apellido) LIKE lower('%{ape}%')
                         ORDER BY id_cliente LIMIT 25""") if ape else None
            if cand is None or cand.empty:
                st.info("Escribe un apellido para buscar.")
                return
            st.dataframe(cand, width="stretch", hide_index=True)
            elegido = int(cand.iloc[0].id_cliente)
            st.caption(f"Se muestra el primero: **{elegido}**")

    ficha = q(f"SELECT * FROM clientes WHERE id_cliente = {elegido}")
    if ficha.empty:
        st.warning("No hay ningún cliente con ese id.")
        return
    f = ficha.iloc[0]
    with der:
        st.markdown(f"### {f.nombre} {f.apellido}")
        a, b, c = st.columns(3)
        a.metric("Segmento", f.segmento)
        b.metric("Ciudad", f.ciudad)
        c.metric("Alta", str(f.fecha_alta))

        r = q(f"""SELECT COUNT(*) AS compras,
                         COALESCE(SUM(unidades*precio_unitario), 0) AS gastado,
                         MIN(fecha) AS primera, MAX(fecha) AS ultima
                  FROM ventas_limpio
                  WHERE id_cliente = {elegido} AND ({donde(filtro)})""").iloc[0]
        a, b, c = st.columns(3)
        a.metric("Compras", es(int(r.compras), 0))
        b.metric("Gastado", f"{es(float(r.gastado))} €")
        b_ticket = float(r.gastado) / int(r.compras) if int(r.compras) else 0
        c.metric("Ticket medio", f"{es(b_ticket)} €")

        if int(r.compras) == 0:
            st.error("**Este cliente no tiene NINGUNA venta con el filtro actual.** "
                     "Si tampoco la tiene sin filtros, es uno de los ausentes del "
                     "LAB07 — y eso vale una llamada comercial.")
        else:
            st.caption(f"Primera compra {r.primera} · última {r.ultima}")
            st.dataframe(q(f"""SELECT v.fecha, v.id_producto, p.nombre, v.categoria,
                                      v.unidades, v.precio_unitario,
                                      ROUND(v.unidades*v.precio_unitario,2) AS importe,
                                      v.canal
                               FROM ventas_limpio v
                               LEFT JOIN productos p ON p.id = v.id_producto
                               WHERE v.id_cliente = {elegido} AND ({donde(filtro, 'v')})
                               ORDER BY v.fecha DESC LIMIT 100"""), width="stretch")

    st.divider()
    st.subheader("Los que no han comprado NUNCA")
    st.caption("El anti-join del LAB07, sobre las tablas completas.")
    aus = q("""SELECT c.id_cliente, c.nombre, c.apellido, c.ciudad, c.segmento
               FROM clientes c
               LEFT JOIN ventas_limpio v ON v.id_cliente = c.id_cliente
               WHERE v.id_venta IS NULL
               ORDER BY c.id_cliente""")
    st.dataframe(aus, width="stretch", hide_index=True)
    st.info(f"**{len(aus)}** clientes sin una sola venta. Con nombre y apellido.")


def pagina_productos(filtro):
    st.subheader("Catálogo y stock")
    d = q(f"""SELECT p.id, p.nombre, p.categoria, p.precio, p.stock_total,
                     COALESCE(SUM(v.unidades), 0) AS unidades_vendidas,
                     ROUND(COALESCE(SUM(v.unidades*v.precio_unitario), 0), 2)
                         AS facturacion
              FROM productos p
              LEFT JOIN ventas_limpio v ON v.id_producto = p.id
                                        AND ({donde(filtro, 'v')})
              GROUP BY p.id, p.nombre, p.categoria, p.precio, p.stock_total
              ORDER BY facturacion DESC""")
    en_catalogo = uno("SELECT COUNT(*) FROM productos")
    if len(d) != en_catalogo:
        st.error(f"**{len(d)} filas para {en_catalogo} productos.** El GROUP BY "
                 "está fundiendo productos distintos: agrupa por la clave "
                 "primaria, no por el nombre.")

    a, b, c = st.columns(3)
    a.metric("Productos en catálogo", es(len(d), 0))
    b.metric("Stock total", es(int(d.stock_total.sum()), 0))
    c.metric("Sin una sola venta", es(int((d.unidades_vendidas == 0).sum()), 0))
    st.dataframe(d, width="stretch", hide_index=True)

    st.subheader("Los diez que más facturan")
    st.plotly_chart(px.bar(d.head(10), x="facturacion", y="nombre",
                           orientation="h").update_yaxes(autorange="reversed"),
                    width="stretch")
    with st.expander("Por categoría"):
        st.dataframe(q(f"""SELECT p.categoria,
                                  COUNT(DISTINCT p.id) AS productos,
                                  SUM(p.stock_total)   AS stock,
                                  ROUND(SUM(v.unidades*v.precio_unitario)/1e6, 2)
                                      AS millones
                           FROM productos p
                           LEFT JOIN ventas_limpio v ON v.id_producto = p.id
                                                     AND ({donde(filtro, 'v')})
                           GROUP BY p.categoria ORDER BY millones DESC"""),
                     width="stretch")



def _tam(ruta):
    """Tamaño en KB de un fichero o de una carpeta de Parquet."""
    if os.path.isdir(ruta):
        return sum(os.path.getsize(os.path.join(ruta, f))
                   for f in os.listdir(ruta)) / 1024
    return os.path.getsize(ruta) / 1024


def pagina_publicacion(filtro):
    """Lo que publicaste en el LAB08, usado como JUEZ de lo que dibuja la app."""
    st.subheader("Lo que hay publicado en `datasets/salida/`")
    if not os.path.isdir(SALIDA):
        st.error("No existe `datasets/salida/`. Ejecuta el LAB10.")
        return

    filas = []
    for n in sorted(os.listdir(SALIDA)):
        r = os.path.join(SALIDA, n)
        filas.append({"fichero": n + ("/" if os.path.isdir(r) else ""),
                      "KB": round(_tam(r), 1),
                      "modificado": time.strftime("%Y-%m-%d %H:%M",
                                                  time.localtime(os.path.getmtime(r)))})
    st.dataframe(pd.DataFrame(filas), width="stretch", hide_index=True)

    st.divider()
    st.subheader("⚓ Verificación cruzada · el CSV publicado contra el cálculo en vivo")
    st.caption("Dos caminos que no se conocen: un COPY de tu cuaderno y una consulta "
               "sobre tu Parquet. Si dan lo mismo, puedes confiar en el dato.")

    if filtro != donde_sin_filtros():
        st.warning("**Tienes filtros puestos.** El fichero publicado es una FOTO de "
                   "todas las ventas; la pantalla es EN VIVO. Para compararlos, "
                   "quita los filtros de la izquierda.")

    hay = False
    for fichero, clave in KPIS.items():
        ruta = os.path.join(SALIDA, fichero)
        if not os.path.exists(ruta):
            continue
        hay = True
        publicado = q(f"SELECT * FROM '{ruta}'")
        if clave == "mes":
            vivo = q("""SELECT STRFTIME(fecha,'%Y-%m') AS mes,
                               ROUND(SUM(unidades*precio_unitario), 2) AS facturacion,
                               COUNT(*) AS operaciones
                        FROM ventas_limpio GROUP BY mes ORDER BY mes""")
        else:
            filtro_nulo = " WHERE ciudad IS NOT NULL" if clave == "ciudad" else ""
            vivo = q(f"""SELECT {clave},
                                ROUND(SUM(unidades*precio_unitario), 2) AS facturacion,
                                COUNT(*) AS operaciones
                         FROM ventas_limpio{filtro_nulo}
                         GROUP BY {clave} ORDER BY facturacion DESC""")

        pub_total = float(publicado["facturacion"].sum())
        viv_total = float(vivo["facturacion"].sum())
        dif = abs(pub_total - viv_total)
        col1, col2 = st.columns([1, 2])
        col1.markdown(f"**{fichero}**")
        col1.caption(f"{len(publicado)} filas publicadas · {len(vivo)} en vivo")
        if dif < 0.01 and len(publicado) == len(vivo):
            col2.success(f"COINCIDE · {es(viv_total)} € por las dos vías")
        else:
            col2.error(f"NO COINCIDE · publicado {es(pub_total)} € · "
                       f"en vivo {es(viv_total)} € · diferencia {es(dif)} €")
            col2.caption("¿El CSV es de antes de reejecutar el pipeline? "
                         "¿O el pipeline ha cambiado? Averígualo: esa pregunta "
                         "es media ingeniería de datos.")

    if not hay:
        st.info("Todavía no hay CSV de KPIs. Los publicas en el LAB08 con `COPY … TO`.")

    st.divider()
    st.subheader("CSV contra Parquet · lo que costó y lo que ocupa")
    comp = []
    for origen_f, parquet_f in (("../datasets/clientes.csv", "clientes.parquet"),
                                ("../datasets/productos.json", "productos.parquet")):
        p = os.path.join(SALIDA, parquet_f)
        if os.path.exists(origen_f) and os.path.exists(p):
            a, b = _tam(origen_f), _tam(p)
            comp.append({"original": os.path.basename(origen_f),
                         "KB original": round(a, 1),
                         "parquet": parquet_f, "KB parquet": round(b, 1),
                         "veces más pequeño": round(a / b, 2) if b else None})
    if comp:
        st.dataframe(pd.DataFrame(comp), width="stretch", hide_index=True)
        st.caption("La misma medición del LAB05, ahora sobre tus otras dos tablas.")
    else:
        st.info("Convierte `clientes` y `productos` a Parquet (el reto del cierre) "
                "y aquí aparecerá la comparación.")


# ═══════════════════════════════════════════════════════════════════════════
# 4 · IA · el prompt se redacta AQUÍ, y se audita AQUÍ
# ═══════════════════════════════════════════════════════════════════════════
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODELO = os.environ.get("GEMINI_MODELO", "gemini-2.0-flash")


def gemini(prompt, temperatura=0.2):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{MODELO}:generateContent?key={API_KEY}")
    cuerpo = {"contents": [{"parts": [{"text": prompt}]}],
              "generationConfig": {"temperature": temperatura}}
    pet = urllib.request.Request(
        url, data=json.dumps(cuerpo).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(pet, timeout=90) as r:
        datos = json.load(r)
    return datos["candidates"][0]["content"]["parts"][0]["text"]


def cifras_verificadas(filtro):
    """Lo único que la IA puede citar. Sale de consultas, no de la cabeza."""
    k = q(f"""SELECT COUNT(*) AS operaciones,
                     ROUND(SUM(unidades*precio_unitario), 2) AS facturacion,
                     ROUND(SUM(unidades*precio_unitario)/COUNT(*), 2) AS ticket_medio,
                     COUNT(DISTINCT id_cliente) AS clientes_activos
              FROM ventas_limpio WHERE {donde(filtro)}""").iloc[0].to_dict()
    k["por_canal"] = q(f"""SELECT canal,
                                  ROUND(SUM(unidades*precio_unitario)/1e6,1) AS millones
                           FROM ventas_limpio WHERE {donde(filtro)}
                           GROUP BY canal ORDER BY millones DESC"""
                       ).to_dict("records")
    k["por_ciudad"] = q(f"""SELECT ciudad,
                                   ROUND(SUM(unidades*precio_unitario)/1e6, 1)
                                       AS millones
                            FROM ventas_limpio
                            WHERE {donde(filtro)} AND ciudad IS NOT NULL
                            GROUP BY ciudad ORDER BY millones DESC LIMIT 5"""
                        ).to_dict("records")
    k["por_mes"] = q(f"""SELECT STRFTIME(fecha,'%Y-%m') AS mes,
                                ROUND(SUM(unidades*precio_unitario)/1e6,2) AS millones
                         FROM ventas_limpio WHERE {donde(filtro)}
                         GROUP BY mes ORDER BY mes""").to_dict("records")
    # Los enteros se quedan ENTEROS. Convertirlo todo a float hacía que la IA
    # escribiera «999.535,0 operaciones» en el informe: media transacción no
    # existe, y un decimal de más delata que nadie ha mirado el dato.
    enteros = ("operaciones", "clientes_activos")
    salida = {}
    for kk, vv in k.items():
        if hasattr(vv, "item"):
            vv = vv.item()
        salida[kk] = int(vv) if kk in enteros else vv
    return salida


PLANTILLA = """ROL: eres analista de datos senior y escribes para dirección.

TAREA: redacta 5 hallazgos, un párrafo cada uno, accionables.

FORMATO: markdown, un titular en negrita por hallazgo.

REGLA: usa EXCLUSIVAMENTE las cifras del CONTEXTO. No inventes ninguna.
Si algo no se puede afirmar con estos datos, dilo."""


def pagina_informe(filtro):
    st.subheader("El informe lo redacta la IA · tú lo firmas")
    st.caption("El prompt se escribe aquí. Las cifras se inyectan desde tus "
               "consultas: la IA no calcula nada.")

    if not API_KEY:
        st.warning("Sin clave. En la terminal: `export GEMINI_API_KEY=…` "
                   "y vuelve a arrancar la aplicación.")

    cifras = cifras_verificadas(filtro)
    izq, der = st.columns([1, 1])

    with izq:
        st.markdown("**Tu prompt** — edítalo y vuelve a generar")
        prompt = st.text_area("Prompt", PLANTILLA, height=260,
                              label_visibility="collapsed")
        temp = st.slider("Temperatura", 0.0, 1.0, 0.2, 0.1,
                         help="Baja = literalidad. Ni el 0 garantiza determinismo.")
        with st.expander("Ver el CONTEXTO que se le inyecta"):
            st.json(cifras)
        generar = st.button("Generar informe", type="primary",
                            disabled=not API_KEY)

    if generar:
        completo = (prompt + "\n\nCONTEXTO (cifras ya verificadas):\n"
                    + json.dumps(cifras, ensure_ascii=False, indent=1))
        with st.spinner("Redactando…"):
            try:
                st.session_state.informe = gemini(completo, temp)
                st.session_state.usadas = cifras
            except urllib.error.HTTPError as e:
                st.session_state.informe = (
                    f"**HTTP {e.code}** — 429 = cuota (espera un minuto) · "
                    f"403/400 = la clave · 404 = el nombre del modelo.")
                st.session_state.usadas = None

    with der:
        if "informe" in st.session_state:
            st.markdown(st.session_state.informe)
            if st.session_state.get("usadas"):
                st.warning(
                    "**AUDÍTALO.** Criterio: cita estas cifras y ninguna más → "
                    + " · ".join(f"{r['canal']} {r['millones']}"
                                 for r in st.session_state.usadas["por_canal"])
                    + f" · ticket {st.session_state.usadas['ticket_medio']}. "
                      "¿Ha inventado algún número? ¿Ha redondeado raro? "
                      "¿Afirma algo que estos datos no sostienen?")
                st.download_button("Descargar el informe",
                                   st.session_state.informe,
                                   file_name="informe.md")
                st.caption("El color es sintaxis de Streamlit: en el `.md` "
                           "descargado se verá `:green[▲ 214,3]` en crudo. "
                           "Los símbolos ▲▼●⚓ sí viajan.")
        else:
            st.info("El informe aparecerá aquí. Léelo con las cifras delante: "
                    "tú eres el juez.")


# ═══════════════════════════════════════════════════════════════════════════
# 5 · ARRANQUE
# ═══════════════════════════════════════════════════════════════════════════
PAGINAS = {
    "Resumen": pagina_resumen,
    "Ventas": pagina_ventas,
    "Clientes": pagina_clientes,
    "Productos": pagina_productos,
    "Publicación": pagina_publicacion,
    "Informe con IA": pagina_informe,
}

st.title("Comercial Aragonesa S.L. · cuadro de mando")
banda_del_ancla()
filtro = barra_lateral()

pestanas = st.tabs(list(PAGINAS))
for pestana, funcion in zip(pestanas, PAGINAS.values()):
    with pestana:
        funcion(filtro)

st.divider()
st.caption("Datos: tu Parquet · Motor: DuckDB · Gráficos: Plotly · "
           "Redacción: Gemini, auditada. Curso Big Data e IA Aplicada · "
           "Formación San Miguel · Zaragoza")
