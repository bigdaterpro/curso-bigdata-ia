#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_datasets.py — la fábrica de datos del curso Big Data e IA Aplicada
Formación San Miguel · Edición Técnica · Bloque 1 · rev. 2

Genera los cuatro datasets sintéticos del curso en ./datasets/ :
  ventas.csv (1.000.000), clientes.csv (100.000), productos.json (480), access.log (500.000)

IMPORTANTE (léelo, alumno curioso):
- random.seed(2026): la semilla fija hace que TODOS los puestos generen datos
  idénticos. Tus resultados deben coincidir con los del manual y con los de tu
  compañero; si no coinciden, el error está en tu análisis, no en los datos.
- La "suciedad" (ciudades vacías, variantes de Zaragoza, precios <= 0) y el
  patrón anómalo del log están PLANTADOS a propósito: son parte de los
  ejercicios. No los "arregles" aquí: arréglalos aguas abajo, como en la vida real.
- Si quieres experimentar modificando este script (es sano), copia el fichero
  con otro nombre y otra carpeta de salida: no rompas la correspondencia entre
  tus datos y las soluciones del curso.
"""

import json
import os
import random

random.seed(2026)
OUT = "datasets"
os.makedirs(OUT, exist_ok=True)

MESES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DIAS_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def fecha_iso(mes, dia):
    return f"2025-{mes:02d}-{dia:02d}"

def fecha_aleatoria():
    m = random.randint(1, 12)
    d = random.randint(1, DIAS_MES[m - 1])
    return fecha_iso(m, d)

# ---------------------------------------------------------------------------
# 1. CATÁLOGO — productos.json (480 productos, 96 por categoría)
# ---------------------------------------------------------------------------
CATS = ["informatica", "hogar", "jardin", "deporte", "papeleria"]

NOMBRES_PROD = {
    "informatica": ["Portátil 15.6", "Portátil 14", "Monitor 27 QHD", "Monitor 24 FHD",
                    "Teclado mecánico", "Ratón inalámbrico", "SSD 1TB NVMe", "SSD 2TB NVMe",
                    "Router WiFi 6", "Switch 8 puertos", "Webcam 1080p", "Dock USB-C",
                    "Impresora láser", "NAS 2 bahías", "Tarjeta gráfica", "Memoria RAM 16GB",
                    "Auriculares USB", "SAI 900VA", "Mini PC", "Disco externo 4TB"],
    "hogar": ["Aspiradora ciclónica", "Robot aspirador", "Batidora de vaso", "Freidora de aire",
              "Cafetera espresso", "Plancha de vapor", "Juego de sartenes", "Olla programable",
              "Ventilador de torre", "Radiador de aceite", "Lámpara de pie", "Juego de toallas",
              "Edredón nórdico", "Set de cuchillos", "Báscula de cocina", "Hervidor eléctrico",
              "Purificador de aire", "Tostadora", "Exprimidor", "Colcha reversible"],
    "jardin": ["Cortacésped eléctrico", "Desbrozadora", "Manguera extensible", "Tijeras de podar",
               "Barbacoa de carbón", "Sombrilla 3m", "Conjunto de terraza", "Hamaca plegable",
               "Motosierra compacta", "Hidrolimpiadora", "Semillas césped 5kg", "Maceta grande",
               "Invernadero balcón", "Riego por goteo", "Farol solar", "Cenador 3x3",
               "Compostador 300L", "Escarificador", "Soplador de hojas", "Banco de jardín"],
    "deporte": ["Bicicleta estática", "Cinta de correr", "Mancuernas 2x10kg", "Esterilla yoga",
                "Banda elástica set", "Balón de fútbol", "Raqueta de pádel", "Zapatillas running",
                "Mochila trekking 40L", "Tienda de campaña", "Saco de dormir", "Patinete urbano",
                "Casco ciclismo", "Guantes de gimnasio", "Cuerda de saltar", "Banco de pesas",
                "Bidón térmico", "Gafas de natación", "Pelota pilates", "Barra dominadas"],
    "papeleria": ["Cuaderno A4 tapa dura", "Pack 10 bolígrafos", "Rotuladores 24 colores",
                  "Archivador palanca", "Grapadora metálica", "Tijeras de oficina",
                  "Papel A4 500 hojas", "Carpeta clasificadora", "Notas adhesivas pack",
                  "Calculadora científica", "Agenda anual", "Lápices HB caja 12",
                  "Subrayadores pack 6", "Cinta correctora", "Pegamento en barra",
                  "Cúter profesional", "Sobres C5 caja", "Marcapáginas magnéticos",
                  "Portaminas 0.5", "Taco de notas"],
}
SUFIJOS = [" Uno", " i5", " Pro", " Plus", " Compact", " XL", " Basic", " 2.0", " Max", " Eco"]
TAGS_POOL = ["oferta-flash", "novedad-2025", "ecologico", "premium", "gama-basica",
             "top-ventas", "ofimatica", "portatil", "exterior", "interior",
             "fitness", "vuelta-al-cole"]

# Precios medios por categoría que el reto del LAB04 debe reproducir (redondeados):
MEDIA_OBJETIVO = {"informatica": 760, "hogar": 179, "jardin": 168, "deporte": 124, "papeleria": 21}
# Nº de productos con precio > 100 por categoría (suman 280, dato del LAB04):
MAYORES_100 = {"informatica": 96, "hogar": 70, "jardin": 68, "deporte": 46, "papeleria": 0}
RANGOS = {  # (rango de precios <=100, rango de precios >100)
    "informatica": ((None, None), (110.0, 1999.0)),
    "hogar": ((12.0, 100.0), (101.0, 480.0)),
    "jardin": ((9.0, 100.0), (101.0, 450.0)),
    "deporte": ((8.0, 100.0), (101.0, 380.0)),
    "papeleria": ((1.0, 55.0), (None, None)),
}

# Identificadores: 480 ids dispersos en P-0001..P-1300. P-1042 y P-0317 existen
# (aparecen en los manuales); P-0259 NO existe (su página dará 404 en el log).
ids_pool = [i for i in range(1, 1301) if i not in (259, 1042, 317)]
ids_prod = random.sample(ids_pool, 478) + [1042, 317]
random.shuffle(ids_prod)

productos = []
asignacion_ids = {}
idx = 0
for cat in CATS:
    for k in range(96):
        pid = ids_prod[idx]; idx += 1
        asignacion_ids.setdefault(cat, []).append(pid)

# P-1042 debe ser informática y P-0317 hogar (ejemplos canónicos del Módulo 2):
def _mueve(pid, cat_destino):
    for c in CATS:
        if pid in asignacion_ids[c] and c != cat_destino:
            asignacion_ids[c].remove(pid)
            otro = asignacion_ids[cat_destino].pop()
            asignacion_ids[c].append(otro)
            asignacion_ids[cat_destino].append(pid)
_mueve(1042, "informatica")
_mueve(317, "hogar")
# P-0317 (34,50 EUR) debe caer en el tramo de precios <= 100 de hogar, que son
# las posiciones a partir de MAYORES_100["hogar"] en la lista de asignación:
lst = asignacion_ids["hogar"]
i317 = lst.index(317)
if i317 < MAYORES_100["hogar"]:
    j = MAYORES_100["hogar"]
    lst[i317], lst[j] = lst[j], lst[i317]

def _precios_categoria(cat):
    """96 precios cuya media redondeada clava el objetivo y con la cuota >100 exacta."""
    n_altos = MAYORES_100[cat]
    bajos_rng, altos_rng = RANGOS[cat]
    precios = []
    for _ in range(n_altos):
        lo, hi = altos_rng
        precios.append(round(random.uniform(lo, hi), 2))
    for _ in range(96 - n_altos):
        lo, hi = bajos_rng
        precios.append(round(random.uniform(lo, hi), 2))
    # Ajuste fino: retocar un precio para que round(media) == objetivo
    objetivo = MEDIA_OBJETIVO[cat]
    suma = round(sum(precios), 2)
    deseada = objetivo * 96  # media exacta = objetivo -> redondeo trivialmente correcto
    delta = round(deseada - suma, 2)
    # repartimos el delta sobre precios del tramo alto (o bajo en papelería)
    i = 0
    while abs(delta) > 0.005:
        paso = max(min(delta, 400.0), -400.0)
        candidato = round(precios[i] + paso, 2)
        lo, hi = (altos_rng if (n_altos and i < n_altos) else bajos_rng)
        candidato = max(lo, min(hi, candidato))
        delta = round(delta - (candidato - precios[i]), 2)
        precios[i] = candidato
        i = (i + 1) % 96
    return precios  # sin barajar: la posición k conserva el tramo (alto: k < n_altos)

catalogo_por_id = {}
for cat in CATS:
    precios = _precios_categoria(cat)
    for k, pid in enumerate(asignacion_ids[cat]):
        base = random.choice(NOMBRES_PROD[cat])
        nombre = base + random.choice(SUFIJOS)
        productos.append({
            "id": f"P-{pid:04d}",
            "nombre": nombre,
            "categoria": cat,
            "precio": precios[k],
            "tags": random.sample(TAGS_POOL, random.randint(1, 3)),
            "stock": {"central": random.randint(1, 60), "tiendas": random.randint(0, 40)},
        })

por_id = {p["id"]: p for p in productos}
# Ejemplos canónicos, tal y como aparecen en el manual del Módulo 2:
por_id["P-1042"].update({"nombre": "Portátil 15.6 i5", "precio": 219.90,
                         "tags": ["ofimatica", "portatil"],
                         "stock": {"central": 14, "tiendas": 6}})
por_id["P-0317"].update({"precio": 34.50})
# Reajustar la media tras forzar los canónicos:
for cat in ("informatica", "hogar"):
    objetivo = MEDIA_OBJETIVO[cat]
    miembros = [p for p in productos if p["categoria"] == cat]
    fijos = {"P-1042", "P-0317"}
    suma = round(sum(p["precio"] for p in miembros), 2)
    delta = round(objetivo * 96 - suma, 2)
    ajustables = [p for p in miembros if p["id"] not in fijos and p["precio"] > 100]
    i = 0
    while abs(delta) > 0.005:
        p = ajustables[i]
        lo, hi = (110.0, 1999.0) if cat == "informatica" else (101.0, 480.0)
        paso = max(min(delta, 300.0), -300.0)
        candidato = max(lo, min(hi, round(p["precio"] + paso, 2)))
        delta = round(delta - (candidato - p["precio"]), 2)
        p["precio"] = candidato
        i = (i + 1) % len(ajustables)

# Exactamente 25 productos sin stock central; 11 de ellos, además, sin stock total.
sin_central = random.sample([p for p in productos if p["id"] not in ("P-1042", "P-0317")], 25)
for j, p in enumerate(sin_central):
    p["stock"]["central"] = 0
    p["stock"]["tiendas"] = 0 if j < 11 else random.randint(1, 25)

random.shuffle(productos)
with open(f"{OUT}/productos.json", "w", encoding="utf-8") as f:
    json.dump(productos, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---------------------------------------------------------------------------
# 2. CLIENTES — clientes.csv (100.000)
# ---------------------------------------------------------------------------
NOMBRES = ["Lucia", "Hugo", "Martina", "Mateo", "Sofia", "Leo", "Julia", "Daniel",
           "Paula", "Pablo", "Emma", "Alvaro", "Sara", "Adrian", "Carla", "Mario",
           "Noa", "Diego", "Vega", "Marcos", "Ana", "Javier", "Irene", "Sergio",
           "Elena", "Ruben", "Marta", "Ivan", "Laura", "Oscar"]
APELLIDOS = ["Garcia", "Lopez", "Martinez", "Sanchez", "Perez", "Gomez", "Martin",
             "Jimenez", "Rodriguez", "Hernandez", "Gonzalez", "Moreno", "Alvarez", "Romero",
             "Alonso", "Gutierrez", "Navarro", "Torres", "Dominguez", "Vazquez",
             "Ramos", "Fernandez", "Serrano", "Blanco", "Molina", "Morales", "Ortega",
             "Delgado", "Castro", "Ortiz", "Rubio", "Marin", "Villanueva", "Iglesias"]
CIUDADES_CLI = ["Zaragoza", "Zaragoza", "Zaragoza", "Zaragoza", "Madrid", "Madrid",
                "Barcelona", "Barcelona", "Huesca", "Huesca", "Teruel", "Valencia",
                "Bilbao", "Sevilla", "Pamplona", "Logrono"]
SEGMENTOS = ["particular", "particular", "particular", "empresa", "premium"]

with open(f"{OUT}/clientes.csv", "w", encoding="utf-8", newline="\n") as f:
    f.write("id_cliente,nombre,apellido,ciudad,fecha_alta,segmento\n")
    for cid in range(1, 100001):
        alta_m = random.randint(1, 12)
        alta = f"20{random.randint(19, 24)}-{alta_m:02d}-{random.randint(1, DIAS_MES[alta_m-1]):02d}"
        f.write(f"{cid},{random.choice(NOMBRES)},{random.choice(APELLIDOS)},"
                f"{random.choice(CIUDADES_CLI)},{alta},{random.choice(SEGMENTOS)}\n")

# ---------------------------------------------------------------------------
# 3. VENTAS — ventas.csv (1.000.000)
# ---------------------------------------------------------------------------
N = 1_000_000
N_ORGANICO = 996_000          # el resto son ventas de "cierre de caja" que cuadran totales

# Recuentos EXACTOS por categoría (los del contador de frecuencias del curso):
CUOTA_CAT = [("jardin", 200487), ("deporte", 200210), ("hogar", 200208),
             ("informatica", 199786), ("papeleria", 199309)]
categorias = []
for cat, k in CUOTA_CAT:
    categorias.extend([cat] * k)
random.shuffle(categorias)

# Las dos primeras filas del fichero son los ejemplos literales de los manuales:
def _fija_pos(pos, cat):
    if categorias[pos] != cat:
        j = next(i for i in range(len(categorias)) if categorias[i] == cat and i != pos)
        categorias[pos], categorias[j] = categorias[j], categorias[pos]
_fija_pos(0, "informatica")
_fija_pos(1, "hogar")

# Suciedad plantada (solo en el tramo orgánico, nunca en las 2 filas canónicas):
poblacion = range(2, N_ORGANICO)
dirt_city = random.sample(poblacion, 3030 + 2004 + 941)
CITY_VACIA = set(dirt_city[:3030])
CITY_MINUS = set(dirt_city[3030:3030 + 2004])
CITY_ESPACIO = set(dirt_city[3030 + 2004:])
PRECIO_MALO = set(random.sample(poblacion, 465))

# Clientes: 4 ids nunca compran (LEFT JOIN de la sesión 4); el resto aparece seguro.
AUSENTES = {1373, 28460, 55011, 93208}
presentes = [c for c in range(1, 100001) if c not in AUSENTES]
random.shuffle(presentes)
# las posiciones 0 y 1 son los clientes canónicos:
presentes.remove(84321); presentes.remove(1294)
clientes_venta = [84321, 1294] + presentes  # 99.996 primeros: cobertura garantizada

CIUDADES_W = [("Zaragoza", 3390), ("Madrid", 1392), ("Barcelona", 1194),
              ("Huesca", 989), ("Valencia", 675), ("Sevilla", 590),
              ("Bilbao", 544), ("Teruel", 450), ("Pamplona", 420), ("Logrono", 356)]
CIUDADES = [c for c, w in CIUDADES_W for _ in range(w)]
CANALES = ["web", "web", "tienda", "tienda", "tienda", "movil"]
UNIDADES = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 4, 5]  # E ≈ 1.94

prod_ids = [p["id"] for p in productos]
precio_de = {p["id"]: p["precio"] for p in productos}

filas = []          # (fecha, id_cliente, id_producto, categoria, unidades, precio_c, ciudad, canal)
ingreso_ciudad = {c: 0 for c, _ in CIUDADES_W}
ingreso_total = 0   # en céntimos

def _anota(ciudad, revenue_c):
    global ingreso_total
    ingreso_total += revenue_c
    if ciudad in ingreso_ciudad:
        ingreso_ciudad[ciudad] += revenue_c

# --- filas canónicas 1 y 2 (idénticas a los manuales) ---
filas.append(("2025-01-02", 84321, "P-1042", "informatica", 2, 21990, "Zaragoza", "web"))
_anota("Zaragoza", 2 * 21990)
filas.append(("2025-01-02", 1294, "P-0317", "hogar", 1, 3450, "Huesca", "tienda"))
_anota("Huesca", 3450)

# --- tramo orgánico ---
for i in range(2, N_ORGANICO):
    cat = categorias[i]
    pid = random.choice(asignacion_ids[cat])
    pid_txt = f"P-{pid:04d}"
    base_c = int(round(precio_de[pid_txt] * 100))
    precio_c = int(round(base_c * random.uniform(0.78, 0.95)))
    if i in PRECIO_MALO:
        precio_c = random.choice([0, 0, -100, -precio_c // 10 or -100])
    if i in CITY_VACIA:
        ciudad = ""
    elif i in CITY_MINUS:
        ciudad = "zaragoza"
    elif i in CITY_ESPACIO:
        ciudad = " Zaragoza"
    else:
        ciudad = random.choice(CIUDADES)
    unidades = random.choice(UNIDADES)
    cliente = clientes_venta[i] if i < len(clientes_venta) else random.choice(clientes_venta)
    filas.append((fecha_aleatoria(), cliente, pid_txt, cat, unidades, precio_c,
                  ciudad, random.choice(CANALES)))
    _anota(ciudad, unidades * precio_c)

# --- tramo de cuadre: 4.000 ventas que llevan cada total a su valor oficial ---
OBJETIVO_TOTAL_C = 42_988_886_470            # 429.888.864,70 €
OBJETIVO_CIUDAD_C = {"Zaragoza": 14_565_027_550,   # 145.650.275,50 €
                     "Madrid":    5_987_266_250,   #  59.872.662,50 €
                     "Barcelona": 5_132_541_950,   #  51.325.419,50 €
                     "Huesca":    4_249_133_550}   #  42.491.335,50 €

def _venta_cuadre(pos, ciudad, unidades, precio_c):
    cat = categorias[pos]
    pid = random.choice(asignacion_ids[cat])
    filas.append((fecha_aleatoria(), random.choice(clientes_venta), f"P-{pid:04d}",
                  cat, unidades, precio_c, ciudad, random.choice(CANALES)))
    _anota(ciudad, unidades * precio_c)

pos = N_ORGANICO

def _reparte(ciudad, objetivo_c, n_filas=None):
    """Emite ventas plausibles (u 1-5, precio 1,20-999,99 EUR) que suman EXACTAMENTE
    objetivo_c céntimos, usando n_filas filas si se indica (si no, ~3.000 EUR/venta)."""
    global pos
    R = objetivo_c
    if n_filas is None:
        n_filas = max(2, R // 300_000 + 1)
    assert n_filas >= 2 and 600 * n_filas <= R <= 480_000 * n_filas, \
        f"reparto inviable en {ciudad}: {R} céntimos en {n_filas} filas"
    # Reservamos una fila de cierre pequeña y repartimos el resto:
    cierre = 60_000
    resto = R - cierre
    n = n_filas - 1
    base, sobra = divmod(resto, n)
    partes = [base + 1] * sobra + [base] * (n - sobra)
    # Jitter que conserva la suma (naturalidad de los importes):
    for _ in range(n):
        i, j = random.randrange(n), random.randrange(n)
        d = random.randint(0, 40_000)
        if partes[i] - d >= 600 and partes[j] + d <= 480_000:
            partes[i] -= d; partes[j] += d
    residuo = 0
    for x in partes:
        u = min(5, (x - 1) // 99_999 + 1)
        p = x // u
        residuo += x - u * p          # céntimos perdidos por el redondeo (0-4)
        _venta_cuadre(pos, ciudad, u, p); pos += 1
    cierre += residuo                 # la fila final absorbe el residuo, exacta
    assert 120 <= cierre <= 99_999
    _venta_cuadre(pos, ciudad, 1, cierre); pos += 1

for ciudad in ("Zaragoza", "Madrid", "Barcelona", "Huesca"):
    hueco = OBJETIVO_CIUDAD_C[ciudad] - ingreso_ciudad[ciudad]
    assert hueco > 0, f"calibración: exceso orgánico en {ciudad} ({hueco})"
    _reparte(ciudad, hueco)

hueco_global = OBJETIVO_TOTAL_C - ingreso_total
faltan = N - len(filas)
assert faltan >= 2, "calibración: las ciudades consumieron todas las filas de cuadre"
_reparte("Teruel", hueco_global, n_filas=faltan)

assert len(filas) == N and ingreso_total == OBJETIVO_TOTAL_C

# Barajamos el contenido (las dos filas canónicas se quedan en cabeza) y numeramos:
cola = filas[2:]
random.shuffle(cola)
filas = filas[:2] + cola

with open(f"{OUT}/ventas.csv", "w", encoding="utf-8", newline="\n") as f:
    f.write("id_venta,fecha,id_cliente,id_producto,categoria,unidades,precio_unitario,ciudad,canal\n")
    for i, (fe, cli, pid, cat, u, pc, ciu, can) in enumerate(filas, start=1):
        f.write(f"{i},{fe},{cli},{pid},{cat},{u},{pc//100}.{abs(pc)%100:02d},{ciu},{can}\n"
                if pc >= 0 else
                f"{i},{fe},{cli},{pid},{cat},{u},-{abs(pc)//100}.{abs(pc)%100:02d},{ciu},{can}\n")

# ---------------------------------------------------------------------------
# 4. LOG — access.log (500.000 líneas, formato Apache combinado simplificado)
# ---------------------------------------------------------------------------
ATACANTE = "185.220.101.34"
RUTAS_ATAQUE = [("/admin", 8563), ("/wp-login.php", 8476), ("/admin/login", 8431),
                ("/phpmyadmin", 8266), ("/.env", 8264)]          # 42.000 exactas
LEGIT_TOTAL = 458_000
CODIGOS_LEGIT = {200: 426_839, 404: 14_267, 301: 13_107, 403: 1_872, 500: 1_915}
# (los 35.000 404 restantes hasta 49.267 son del atacante: 7.000 por ruta)

def ts(mes, dia, h, mi, s):
    return f"{dia:02d}/{MESES[mes-1]}/2025:{h:02d}:{mi:02d}:{s:02d} +0100"

def ts_aleatorio(horas=None):
    m = random.randint(1, 12)
    d = random.randint(1, DIAS_MES[m - 1])
    h = random.choice(horas) if horas else random.randint(0, 23)
    return (m, d, h, random.randint(0, 59), random.randint(0, 59))

def clave(t):  # orden cronológico
    m, d, h, mi, s = t
    return (m, d, h, mi, s)

lineas = []  # (clave_orden, texto)

# --- tráfico del atacante: 10–14 de febrero ---
def ts_ataque():
    return (2, random.randint(10, 14), random.randint(0, 23),
            random.randint(0, 59), random.randint(0, 59))

for ruta, total in RUTAS_ATAQUE:
    codigos = [404] * 7000 + [403] * 900 + [301] * (total - 7900)
    random.shuffle(codigos)
    metodo = "POST" if "login" in ruta else "GET"
    for c in codigos:
        t = ts_ataque()
        m, d, h, mi, s = t
        lineas.append((clave(t),
            f'{ATACANTE} - - [{ts(m, d, h, mi, s)}] "{metodo} {ruta} HTTP/1.1" {c} {random.randint(200, 900)}'))

# --- pool de IPs legítimas: la más activa hace exactamente 520 peticiones ---
def ip_aleatoria():
    return f"{random.randint(2, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

TOP_LEGIT = "83.52.101.7"      # la IP del ejemplo del manual
cuotas_ip = [(TOP_LEGIT, 519)]      # +1 canónica del manual = 520 exactas
restante_ip = LEGIT_TOTAL - 1 - 519
while restante_ip > 0:
    n = min(random.randint(40, 480), restante_ip)
    cuotas_ip.append((ip_aleatoria(), n))
    restante_ip -= n
bolsa_ips = [ip for ip, n in cuotas_ip for _ in range(n)]
random.shuffle(bolsa_ips)

# --- rutas legítimas ---
RUTAS_200 = ([f"/producto/{p}" for p in prod_ids] * 6 +
             ["/", "/", "/", "/carrito", "/checkout", "/buscar", "/login", "/mi-cuenta",
              "/static/app.css", "/static/app.js", "/static/logo.png"] * 120 +
             [f"/categoria/{c}" for c in CATS] * 150)
RUTAS_301 = ["/index.php", "/home", "/tienda", "/producto-antiguo", "/promo-2024"] 
RUTAS_403 = ["/mi-cuenta/facturas", "/interno", "/api/admin"]
# 404 legítimos: productos retirados; P-0259 es el nº1 con 46 peticiones
retirados = sorted(set(range(1, 1301)) - set(ids_prod))
rutas_404 = []
r404 = CODIGOS_LEGIT[404] - 46
pool_muertos = [f"/producto/P-{x:04d}" for x in retirados if x != 259]
random.shuffle(pool_muertos)
for ruta in pool_muertos:
    if r404 <= 0:
        break
    n = min(random.randint(5, 45), r404)
    rutas_404.extend([ruta] * n)
    r404 -= n
i_extra = 0
while r404 > 0:                      # relleno seguro por si el pool se agota
    rutas_404.append(f"/img/banner-{i_extra}.png"); r404 -= 1; i_extra += 1
    if i_extra > 45: i_extra = 0
rutas_404.extend(["/producto/P-0259"] * 46)
random.shuffle(rutas_404)

# --- horas de los errores 500: 1.609 a las 03h (84%), 28 a las 15h, 26 a las 19h ---
horas_500 = [3] * 1609 + [15] * 28 + [19] * 26
r500 = CODIGOS_LEGIT[500] - len(horas_500)
otras = [h for h in range(24) if h not in (3, 15, 19)]
cuotas = {h: 0 for h in otras}
while r500 > 0:
    h = random.choice(otras)
    if cuotas[h] < 25:
        cuotas[h] += 1; horas_500.append(h); r500 -= 1
random.shuffle(horas_500)

ip_idx = 0
def siguiente_ip():
    global ip_idx
    ip = bolsa_ips[ip_idx]; ip_idx += 1
    return ip

for _ in range(CODIGOS_LEGIT[200] - 1):
    t = ts_aleatorio(); m, d, h, mi, s = t
    lineas.append((clave(t),
        f'{siguiente_ip()} - - [{ts(m, d, h, mi, s)}] "GET {random.choice(RUTAS_200)} HTTP/1.1" 200 {random.randint(300, 95000)}'))
# la línea canónica del manual (cuenta como petición de 83.52.101.7):
lineas.append((clave((2, 12, 18, 33, 1)),
    '83.52.101.7 - - [12/Feb/2025:18:33:01 +0100] "GET /producto/P-1042 HTTP/1.1" 200 5123'))

for ruta in rutas_404:
    t = ts_aleatorio(); m, d, h, mi, s = t
    lineas.append((clave(t),
        f'{siguiente_ip()} - - [{ts(m, d, h, mi, s)}] "GET {ruta} HTTP/1.1" 404 {random.randint(180, 1200)}'))
for _ in range(CODIGOS_LEGIT[301]):
    t = ts_aleatorio(); m, d, h, mi, s = t
    lineas.append((clave(t),
        f'{siguiente_ip()} - - [{ts(m, d, h, mi, s)}] "GET {random.choice(RUTAS_301)} HTTP/1.1" 301 {random.randint(150, 400)}'))
for _ in range(CODIGOS_LEGIT[403]):
    t = ts_aleatorio(); m, d, h, mi, s = t
    lineas.append((clave(t),
        f'{siguiente_ip()} - - [{ts(m, d, h, mi, s)}] "GET {random.choice(RUTAS_403)} HTTP/1.1" 403 {random.randint(150, 500)}'))
for h500 in horas_500:
    m = random.randint(1, 12); d = random.randint(1, DIAS_MES[m - 1])
    t = (m, d, h500, random.randint(0, 59), random.randint(0, 59))
    lineas.append((clave(t),
        f'{siguiente_ip()} - - [{ts(*t)}] "GET {random.choice(RUTAS_200)} HTTP/1.1" 500 {random.randint(200, 600)}'))

lineas.sort(key=lambda x: x[0])
with open(f"{OUT}/access.log", "w", encoding="utf-8", newline="\n") as f:
    for _, txt in lineas:
        f.write(txt + "\n")

print(f"productos.json: {len(productos)} productos · clientes.csv: 100000 · "
      f"ventas.csv: {N} · access.log: {len(lineas)}")
