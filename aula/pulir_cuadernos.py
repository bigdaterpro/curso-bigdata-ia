#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pulir_cuadernos.py — audita y repara cuadernos del curso, sin tocar lo que importa
Formación San Miguel · Big Data e IA Aplicada · Edición Técnica · rev. 2

    python3 aula/pulir_cuadernos.py notebooks/*.ipynb                    # informe
    python3 aula/pulir_cuadernos.py --arreglar notebooks/*.ipynb         # corrige
    python3 aula/pulir_cuadernos.py --arreglar --imports notebooks/*.ipynb
    python3 aula/pulir_cuadernos.py --arreglar --copia notebooks/*.ipynb # deja .bak

Pensado para pasarlo sobre un cuaderno QUE YA HAS EDITADO A MANO: solo actúa donde
encuentra el defecto y deja intacto todo lo demás.

────────────────────────────────────────────────────────────────────────────────
QUÉ ARREGLA SOLO

  MD1 tabla partida ....... un blanco entre dos filas: deja de ser tabla y el
                            alumno ve literalmente «| --- | --- |»
  MD2 párrafo roto ........ un blanco a mitad de frase: se ve cortada en dos
  MD3 lista suelta ........ un blanco entre viñetas: renderiza, pero desparejada
  MD4 tubería mal escapada  «&#124;» dentro de un span de código sale tal cual;
                            en una fila de tabla la forma correcta es  \\|
  MD5 cita partida ........ un blanco entre dos líneas «> »: cada una se
                            convierte en UNA CITA DISTINTA
  MD6 tabla sin separadora  una tabla sin la fila «|---|---|» no es tabla
  MD7 lista pegada ........ una viñeta pegada al párrafo anterior, sin blanco
  MD9 viñeta partida ...... un blanco entre una viñeta y su línea de continuación
                            sangrada: la lista se vuelve «suelta» y el segundo
                            renglón se separa como un párrafo aparte
  MD8 blancos repetidos ... tres o más blancos seguidos dentro de una celda

  CO1 espacios en cola .... invisibles, ensucian el diff
  CO2 tabulaciones ........ se ven distinto en cada editor; a 4 espacios
  CO3 blancos de los bordes  al principio y al final de la celda
  CO4 BLANCO ESPURIO ...... una línea en blanco dentro de una celda de CÓDIGO,
                            en un sitio donde no puede ser un separador: dentro
                            de una cadena, dentro de un paréntesis, entre dos
                            comentarios seguidos, o tras una continuación «\\».
                            Es el MD2 del código: parte una consulta SQL por la
                            mitad, o trocea un bloque de comentarios
  CO5 blancos repetidos ... dos o más blancos seguidos en una celda de código
  CO6 import ausente ...... solo con --imports: la celda usa duckdb, os, re… y
                            no lo importa. Se añade arriba, y así la celda se
                            puede ejecutar suelta tras un «Restart Kernel»

  NB1 source normalizado .. cada línea con su \\n, menos la última
  NB2 identificadores ..... celdas sin «id» en nbformat 4.5
  NB3 metadatos de ruido .. collapsed, scrolled, jupyter.outputs_hidden…

QUÉ SOLO INFORMA  (aquí hace falta criterio humano)

  AV1 línea de código larga  Jupyter la ENVUELVE. Se reescribe a mano: dónde
                             parte una consulta es una decisión de legibilidad
  AV2 valla ``` sin cerrar   rompe el resto de la celda
  AV3 negritas impares       un ** suelto se ve en crudo
  AV4 celda vacía            ruido en el HTML del entregable
  AV5 posible clave de API   patrón AIza…  ->  -10 en la rúbrica
  AV6 salida sin ejecución   outputs guardados sin execution_count

QUÉ NO TOCA NUNCA: las salidas, los números de ejecución, el nbformat ni los
metadatos del cuaderno. Y el código solo cambia de FORMA: al terminar se compara
el árbol de sintaxis (AST) de cada celda con el de antes, y se dice en pantalla.
"""
import ast
import json
import os
import re
import sys
import uuid

FILA = re.compile(r"^\s*\|.*\|\s*$")
SEPARADORA = re.compile(r"^\s*\|[\s:|-]*-{2,}[\s:|-]*\|?\s*$")
VINETA = re.compile(r"^\s*([-*+]|\d+\.) +\S")
VALLA = re.compile(r"^\s*```")
ESPECIAL = ("|", "#", ">", "```", "---", "===")
FIN_DE_FRASE = re.compile(r"[.:;!?»)\]…]\s*$")
FIN_FUERTE = re.compile(r"[.?!…][\"'»)\]]*\s*$")
CLAVE = re.compile(r"AIza[0-9A-Za-z_\-]{20,}")

ANCHO_CODIGO = 88
RUIDO_META = ("collapsed", "scrolled", "jupyter", "tags_hidden")
COMILLA3 = ('"' * 3, "'" * 3)

IMPORTES = {
    "duckdb": "import duckdb", "os": "import os", "json": "import json",
    "re": "import re", "glob": "import glob", "shutil": "import shutil",
    "zipfile": "import zipfile", "sys": "import sys", "time": "import time",
    "socket": "import socket", "signal": "import signal",
    "subprocess": "import subprocess", "px": "import plotly.express as px",
    "pd": "import pandas as pd",
    "F": "from pyspark.sql import functions as F",
}

ARREGLA = ["md1_tabla", "md2_parrafo", "md3_lista", "md4_tuberia", "md5_cita",
           "md6_separadora", "md7_pegada", "md8_repetido", "md9_vineta",
           "co1_cola", "co2_tabs", "co3_bordes", "co4_espurio", "co5_repetido",
           "co6_import", "nb1_source", "nb2_id", "nb3_meta"]
AVISA = ["av1_larga", "av2_valla", "av3_negrita", "av4_vacia", "av5_clave",
         "av6_sin_ejecutar"]

NOMBRES = {
    "md1_tabla": "tabla partida", "md2_parrafo": "párrafo roto",
    "md3_lista": "lista suelta", "md4_tuberia": "tubería mal escapada",
    "md5_cita": "cita partida", "md6_separadora": "tabla sin separadora",
    "md7_pegada": "lista pegada", "md8_repetido": "blancos repetidos (md)", "md9_vineta": "viñeta partida",
    "co1_cola": "espacios en cola", "co2_tabs": "tabulaciones",
    "co3_bordes": "blancos en los bordes", "co4_espurio": "BLANCO ESPURIO",
    "co5_repetido": "blancos repetidos", "co6_import": "import añadido",
    "nb1_source": "source sin normalizar", "nb2_id": "celda sin id",
    "nb3_meta": "metadatos de ruido", "av1_larga": "línea larga (envuelve)",
    "av2_valla": "valla ``` sin cerrar", "av3_negrita": "negritas impares",
    "av4_vacia": "celda vacía", "av5_clave": "posible clave de API",
    "av6_sin_ejecutar": "salidas sin ejecución",
}


def nuevo_contador():
    return {k: 0 for k in ARREGLA + AVISA}


def lineas_de(celda):
    src = celda["source"]
    return ("".join(src) if isinstance(src, list) else src).split("\n")


def guardar(celda, lineas):
    celda["source"] = [l + "\n" for l in lineas[:-1]] + [lineas[-1]]


# ── MD4 · tuberías ──────────────────────────────────────────────────────────
def escapar_tuberias(linea):
    if not FILA.match(linea):
        return linea, 0
    original = linea
    linea = re.sub(r"<code>((?:&#124;)+)</code>",
                   lambda m: "\\|" * (len(m.group(1)) // 6), linea)
    linea = linea.replace("&#124;", "\\|")

    def dentro_del_span(m):
        return "`" + m.group(1).replace("\\|", "|").replace("|", "\\|") + "`"

    linea = re.sub(r"`([^`]*)`", dentro_del_span, linea)
    return linea, (1 if linea != original else 0)


# ── celdas Markdown ─────────────────────────────────────────────────────────
def revisar_markdown(lineas, inc):
    salida = []
    for l in lineas:
        nueva, tocada = escapar_tuberias(l)
        inc["md4_tuberia"] += tocada
        salida.append(nueva)
    lineas = salida

    salida, i = [], 0
    while i < len(lineas):
        l = lineas[i]
        salida.append(l)
        j, blancos = i + 1, 0
        while j < len(lineas) and lineas[j].strip() == "":
            blancos += 1
            j += 1
        if blancos and j < len(lineas):
            siguiente = lineas[j]
            if l.lstrip().startswith(">") and siguiente.lstrip().startswith(">"):
                cuerpo = siguiente.lstrip()[1:].lstrip()
                anterior = re.sub(r"[*_`]+\s*$", "", l).rstrip()
                inc["md5_cita"] += 1
                if (cuerpo[:1].islower() or l.strip() == ">" or cuerpo == ""
                        or not FIN_FUERTE.search(anterior)):
                    i = j
                    continue
                sangria = l[:len(l) - len(l.lstrip())]
                salida.append(sangria + ">")
                i = j
                continue
            pega = None
            # MD9 · una viñeta y su continuación sangrada, separadas por un blanco
            if (blancos == 1 and siguiente.startswith("  ")
                    and siguiente.strip() and not VINETA.match(siguiente)
                    and not siguiente.lstrip().startswith(ESPECIAL)
                    and (VINETA.match(l) or l.startswith("  ")) and l.strip()):
                inc["md9_vineta"] += 1
                i = j
                continue
            if FILA.match(l) and FILA.match(siguiente):
                pega = "md1_tabla"
            elif VINETA.match(l) and VINETA.match(siguiente):
                pega = "md3_lista"
            elif (l.strip() and not l.lstrip().startswith(ESPECIAL)
                  and not VINETA.match(l)
                  and not FIN_DE_FRASE.search(re.sub(r"[*_`]+\s*$", "", l))
                  and siguiente.strip()
                  and not siguiente.lstrip().startswith(ESPECIAL)
                  and not VINETA.match(siguiente)
                  and not siguiente.lstrip()[:1].isupper()
                  and blancos == 1):
                pega = "md2_parrafo"
            if pega:
                inc[pega] += 1
                i = j
                continue
        i += 1
    lineas = salida

    salida, i, en_valla = [], 0, False
    while i < len(lineas):
        l = lineas[i]
        if VALLA.match(l):
            en_valla = not en_valla
        if not en_valla:
            empieza = (FILA.match(l) and not SEPARADORA.match(l)
                       and (not salida or not FILA.match(salida[-1])))
            if (empieza and i + 1 < len(lineas) and FILA.match(lineas[i + 1])
                    and not SEPARADORA.match(lineas[i + 1])):
                salida.append(l)
                n = len(l.strip().strip("|").split("|"))
                salida.append("|" + "|".join(["---"] * n) + "|")
                inc["md6_separadora"] += 1
                i += 1
                continue
            if (VINETA.match(l) and salida and salida[-1].strip()
                    and not VINETA.match(salida[-1])
                    and not salida[-1].lstrip().startswith(ESPECIAL)):
                salida.append("")
                inc["md7_pegada"] += 1
        salida.append(l)
        i += 1
    lineas = salida

    salida, en_valla = [], False
    for k, l in enumerate(lineas):
        if VALLA.match(l):
            en_valla = not en_valla
        if (not en_valla and l.strip() == "" and len(salida) >= 2
                and salida[-1].strip() == "" and salida[-2].strip() == ""
                and any(x.strip() for x in lineas[k + 1:])):
            inc["md8_repetido"] += 1
            continue
        salida.append(l)
    return salida, inc


# ── celdas de código ────────────────────────────────────────────────────────
def estados_codigo(lineas):
    """Estado ANTES de cada línea: (paréntesis abiertos, dentro de cadena).

    Es lo que permite distinguir un separador legítimo de un blanco que está
    partiendo una consulta SQL por la mitad.
    """
    prof, triple, out = 0, None, []
    for l in lineas:
        out.append((prof, triple is not None))
        i = 0
        while i < len(l):
            c = l[i]
            if triple:
                if l.startswith(triple, i):
                    triple, i = None, i + 3
                    continue
                i += 1
                continue
            if c == "#":
                break
            if l.startswith(COMILLA3, i):
                triple, i = l[i:i + 3], i + 3
                continue
            if c in "\"'":
                q, i = c, i + 1
                while i < len(l):
                    if l[i] == "\\":
                        i += 2
                        continue
                    if l[i] == q:
                        i += 1
                        break
                    i += 1
                continue
            if c in "([{":
                prof += 1
            elif c in ")]}":
                prof = max(0, prof - 1)
            i += 1
    return out


def revisar_codigo(lineas, inc):
    est = estados_codigo(lineas)
    salida = []
    for k, l in enumerate(lineas):
        if l.strip() != "" or k in (0, len(lineas) - 1):
            salida.append(l)
            continue
        ant, sig = lineas[k - 1], lineas[k + 1]
        prof, en_cadena = est[k]
        if ant.strip() and sig.strip() and (
                en_cadena or prof > 0
                or (ant.lstrip().startswith("#") and sig.lstrip().startswith("#"))
                or ant.rstrip().endswith("\\")):
            inc["co4_espurio"] += 1
            continue
        if salida and salida[-1].strip() == "":
            inc["co5_repetido"] += 1
            continue
        salida.append(l)
    return salida, inc


def falta_importar(fuente):
    """Módulos que la celda usa y no importa. Con AST, no con expresiones."""
    limpio = "\n".join(l for l in fuente.split("\n")
                       if not l.lstrip().startswith(("%", "!")))
    try:
        arbol = ast.parse(limpio)
    except SyntaxError:
        return []
    dentro = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for a in nodo.names:
                dentro.add((a.asname or a.name).split(".")[0])
        elif isinstance(nodo, ast.ImportFrom):
            for a in nodo.names:
                dentro.add(a.asname or a.name)
    usados = {n.id for n in ast.walk(arbol) if isinstance(n, ast.Name)}
    return [m for m in IMPORTES if m in usados and m not in dentro]


# ── avisos ──────────────────────────────────────────────────────────────────
def avisar(celda, lineas, inc, detalle, n, ancho):
    texto = "\n".join(lineas)
    if texto.count("```") % 2:
        inc["av2_valla"] += 1
        detalle.append((n, "valla ``` sin cerrar"))
    if celda["cell_type"] == "markdown" and texto.count("**") % 2:
        inc["av3_negrita"] += 1
        detalle.append((n, "negritas ** impares"))
    if not texto.strip():
        inc["av4_vacia"] += 1
        detalle.append((n, "celda vacía"))
    for k, l in enumerate(lineas):
        if CLAVE.search(l) and not l.lstrip().startswith("#"):
            inc["av5_clave"] += 1
            detalle.append((n, f"línea {k + 1}: posible clave de API"))
    if celda["cell_type"] == "code":
        for k, l in enumerate(lineas):
            if len(l) > ancho:
                inc["av1_larga"] += 1
                detalle.append((n, f"línea {k + 1}: {len(l)} caracteres"))
        if celda.get("outputs") and celda.get("execution_count") is None:
            inc["av6_sin_ejecutar"] += 1
            detalle.append((n, "salidas sin número de ejecución"))
    else:
        dentro = False
        for k, l in enumerate(lineas):
            if VALLA.match(l):
                dentro = not dentro
                continue
            if dentro and len(l) > ancho - 4:
                inc["av1_larga"] += 1
                detalle.append((n, f"línea {k + 1} (dentro de ```): {len(l)} car."))
    return inc, detalle


# ── un cuaderno ─────────────────────────────────────────────────────────────
def procesar(ruta, arreglar=False, ancho=ANCHO_CODIGO, copia=False, imports=False):
    original = open(ruta, encoding="utf-8").read()
    nb = json.loads(original)
    inc, detalle = nuevo_contador(), []

    for n, celda in enumerate(nb["cells"]):
        lineas = lineas_de(celda)
        es_codigo = celda["cell_type"] == "code"

        if es_codigo:
            lineas, inc = revisar_codigo(lineas, inc)
        elif celda["cell_type"] == "markdown":
            lineas, inc = revisar_markdown(lineas, inc)

        limpias = []
        for l in lineas:
            l2 = l.replace("\t", "    ")
            if l2 != l:
                inc["co2_tabs"] += 1
            l3 = l2.rstrip()
            if l3 != l2:
                inc["co1_cola"] += 1
            limpias.append(l3)
        lineas = limpias

        # CO3 · bordes. En Markdown se conservan hasta dos blancos al final:
        # son el espacio donde el alumnado escribe debajo de un ✍️.
        antes = len(lineas)
        while lineas and lineas[0].strip() == "":
            lineas.pop(0)
        cola = 0 if es_codigo else 2
        while len(lineas) > cola and all(x.strip() == "" for x in lineas[-cola - 1:]):
            lineas.pop()
        if len(lineas) != antes:
            inc["co3_bordes"] += antes - len(lineas)
        if not lineas:
            lineas = [""]

        if es_codigo and imports:
            faltan = falta_importar("\n".join(lineas))
            if faltan:
                cabecera = sorted(IMPORTES[m] for m in faltan)
                inc["co6_import"] += len(cabecera)
                if arreglar:
                    lineas = cabecera + [""] + lineas

        inc, detalle = avisar(celda, lineas, inc, detalle, n, ancho)

        if celda.get("source") != [l + "\n" for l in lineas[:-1]] + [lineas[-1]]:
            inc["nb1_source"] += 1
        if arreglar:
            guardar(celda, lineas)

        if nb.get("nbformat_minor", 0) >= 5 and not celda.get("id"):
            inc["nb2_id"] += 1
            if arreglar:
                celda["id"] = uuid.uuid4().hex[:8]

        meta = celda.get("metadata", {})
        sobra = [k for k in list(meta) if k in RUIDO_META]
        if sobra:
            inc["nb3_meta"] += len(sobra)
            if arreglar:
                for k in sobra:
                    meta.pop(k, None)

    if arreglar and any(inc[k] for k in ARREGLA):
        if copia:
            open(ruta + ".bak", "w", encoding="utf-8").write(original)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
            f.write("\n")
    return inc, detalle, original


# ── la comprobación que cierra el trabajo ───────────────────────────────────
def _ast_normalizado(fuente):
    limpio = "\n".join(l for l in fuente.split("\n")
                       if not l.lstrip().startswith(("%", "!")))
    arbol = ast.parse(limpio)
    for x in ast.walk(arbol):
        if isinstance(x, ast.Constant) and isinstance(x.value, str):
            # un salto de línea dentro de un SQL no cambia lo que hace
            x.value = re.sub(r"\s+", " ", x.value).strip()
    # los import añadidos con --imports no son un cambio de semántica
    arbol.body = [n for n in arbol.body
                  if not isinstance(n, (ast.Import, ast.ImportFrom))]
    return ast.dump(arbol)


def comprobar_intacto(ruta, original):
    a, b = json.loads(original), json.load(open(ruta, encoding="utf-8"))
    if len(a["cells"]) != len(b["cells"]):
        return "CAMBIÓ EL NÚMERO DE CELDAS"
    ca = [c for c in a["cells"] if c["cell_type"] == "code"]
    cb = [c for c in b["cells"] if c["cell_type"] == "code"]
    if [c.get("outputs") for c in ca] != [c.get("outputs") for c in cb]:
        return "CAMBIARON LAS SALIDAS"
    if [c.get("execution_count") for c in ca] != [c.get("execution_count") for c in cb]:
        return "CAMBIARON LOS NÚMEROS DE EJECUCIÓN"
    if a.get("metadata") != b.get("metadata") or a["nbformat"] != b["nbformat"]:
        return "CAMBIARON LOS METADATOS DEL CUADERNO"
    for i, (x, y) in enumerate(zip(ca, cb)):
        try:
            if _ast_normalizado("".join(x["source"])) != \
               _ast_normalizado("".join(y["source"])):
                return f"CAMBIÓ LA SEMÁNTICA DEL CÓDIGO (celda de código {i})"
        except SyntaxError as e:
            return f"EL CÓDIGO NO COMPILA (celda de código {i}): {e}"
    return None


def main():
    args = sys.argv[1:]
    arreglar = "--arreglar" in args
    copia = "--copia" in args
    imports = "--imports" in args
    ancho = ANCHO_CODIGO
    for a in args:
        if a.startswith("--ancho="):
            ancho = int(a.split("=")[1])
    ficheros = [a for a in args if not a.startswith("--")]
    if not ficheros:
        print(__doc__)
        return 2

    print(f"{'cuaderno':30} {'arreglado':>10} {'revisar':>8}   detalle")
    print("-" * 78)
    total_arr = total_avi = 0
    pendientes, roto = [], False
    for f in ficheros:
        inc, detalle, original = procesar(f, arreglar, ancho, copia, imports)
        arr = sum(inc[k] for k in ARREGLA)
        avi = sum(inc[k] for k in AVISA)
        total_arr, total_avi = total_arr + arr, total_avi + avi
        resumen = ", ".join(f"{inc[k]} {NOMBRES[k]}"
                            for k in ARREGLA + AVISA if inc[k])
        print(f"{os.path.basename(f):30} {arr:>10} {avi:>8}   {resumen}")
        if arreglar:
            mal = comprobar_intacto(f, original)
            if mal:
                roto = True
                print(f"    !! {mal} — restaura desde git y avisa")
        for n, msg in detalle:
            pendientes.append((os.path.basename(f), n, msg))

    print("-" * 78)
    if pendientes:
        print("\nPOR REVISAR A MANO (el script no los toca a propósito):")
        for f, n, msg in pendientes:
            print(f"    {f:30} celda {n:>3}: {msg}")
        print("\n  Las líneas largas se reescriben a mano: partirlas es una decisión")
        print("  de legibilidad y eso no lo automatizo.")

    print()
    if arreglar and not roto:
        print("Comprobado: salidas, números de ejecución, metadatos y semántica")
        print("del código, INTACTOS en todos los cuadernos.")
    if not total_arr and not total_avi:
        print("Sin incidencias: estos cuadernos están limpios.")
    elif arreglar:
        print(f"{total_arr} incidencias corregidas · {total_avi} por revisar a mano.")
    else:
        print(f"{total_arr} corregibles · {total_avi} por revisar a mano.")
        print("Vuelve a pasarlo con --arreglar (y --copia si quieres un .bak).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
