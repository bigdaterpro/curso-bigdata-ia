#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verificar_cuadernos.py — comprueba un cuaderno de arriba abajo, con lógica propia
Formación San Miguel · Big Data e IA Aplicada · Edición Técnica

    python3 aula/verificar_cuadernos.py notebooks/*.ipynb
    python3 aula/verificar_cuadernos.py --contra originales/ notebooks/*.ipynb

Este NO es el reparador: es el juez. No comparte código con `pulir_cuadernos.py`
a propósito — si los dos usaran las mismas funciones, los dos tendrían los mismos
puntos ciegos. Aquí se vuelve a mirar todo, desde cero.

Dieciséis pruebas, en tres familias:

  ESTRUCTURA        1 JSON válido y nbformat coherente
                    2 todas las celdas con id (nbformat 4.5)
                    3 sin metadatos de ruido
                    4 sin celdas vacías
  CÓDIGO            5 cada celda compila (ast.parse)
                    6 sin líneas de más de 88 caracteres
                    7 sin blancos espurios (dentro de cadena o paréntesis,
                      entre comentarios, tras una continuación)
                    8 sin dos blancos seguidos
                    9 sin espacios en cola ni tabulaciones
                   10 cada celda importa lo que usa
                   11 ninguna clave de API a la vista
  MARKDOWN         12 renderiza sin '**' ni comillas invertidas sueltas
                   13 sin tablas partidas ni tablas sin fila separadora
                   14 sin citas partidas
                   15 sin listas partidas (entre viñetas o en su continuación)
                   16 sin líneas de más de 84 caracteres dentro de ```

Con --contra, además: mismo número de celdas, mismas salidas, mismos números de
ejecución y misma semántica del código (AST) que el original.
"""
import ast
import json
import os
import re
import sys

ANCHO_CODIGO = 88
ANCHO_VALLA = 84
RUIDO_META = ("collapsed", "scrolled", "jupyter", "tags_hidden")
CLAVE = re.compile(r"AIza[0-9A-Za-z_\-]{20,}")
FILA = re.compile(r"^\s*\|.*\|\s*$")
SEPARADORA = re.compile(r"^\s*\|[\s:|-]*-{2,}[\s:|-]*\|?\s*$")
VINETA = re.compile(r"^\s*([-*+]|\d+\.) +\S")
VALLA = re.compile(r"^\s*```")
MODULOS = ("duckdb", "os", "json", "re", "glob", "shutil", "zipfile", "sys",
           "time", "socket", "signal", "subprocess", "px", "pd", "F")


def lineas(celda):
    src = celda["source"]
    return ("".join(src) if isinstance(src, list) else src).split("\n")


def sin_magias(texto):
    return "\n".join(l for l in texto.split("\n")
                     if not l.lstrip().startswith(("%", "!")))


# ── análisis léxico propio: dónde está cada línea del código ────────────────
def estado_por_linea(ls):
    prof, triple, out = 0, None, []
    for l in ls:
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
            if l.startswith(('"""', "'''"), i):
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


def ast_normalizado(fuente):
    arbol = ast.parse(sin_magias(fuente))
    for x in ast.walk(arbol):
        if isinstance(x, ast.Constant) and isinstance(x.value, str):
            x.value = re.sub(r"\s+", " ", x.value).strip()
    arbol.body = [n for n in arbol.body
                  if not isinstance(n, (ast.Import, ast.ImportFrom))]
    return ast.dump(arbol)


def revisar(ruta):
    fallos = []

    def mal(prueba, celda, msg):
        fallos.append((prueba, celda, msg))

    try:
        nb = json.load(open(ruta, encoding="utf-8"))
    except Exception as e:
        return [("1 JSON", "-", str(e))]
    if "cells" not in nb or "nbformat" not in nb:
        return [("1 JSON", "-", "faltan claves básicas")]

    for n, celda in enumerate(nb["cells"]):
        ls = lineas(celda)
        texto = "\n".join(ls)
        es_codigo = celda["cell_type"] == "code"

        if nb.get("nbformat_minor", 0) >= 5 and not celda.get("id"):
            mal("2 id", n, "celda sin identificador")
        for k in celda.get("metadata", {}):
            if k in RUIDO_META:
                mal("3 metadatos", n, f"metadato de ruido: {k}")
        if not texto.strip():
            mal("4 vacía", n, "celda vacía")
        for k, l in enumerate(ls):
            if l.rstrip() != l:
                mal("9 blancos", n, f"línea {k + 1}: espacios en cola")
            if "\t" in l:
                mal("9 blancos", n, f"línea {k + 1}: tabulación")
            if CLAVE.search(l) and not l.lstrip().startswith("#"):
                mal("11 clave", n, f"línea {k + 1}: posible clave de API")

        if es_codigo:
            try:
                arbol = ast.parse(sin_magias(texto))
            except SyntaxError as e:
                mal("5 compila", n, f"{e}")
                continue
            for k, l in enumerate(ls):
                if len(l) > ANCHO_CODIGO:
                    mal("6 línea larga", n, f"línea {k + 1}: {len(l)} caracteres")
            est = estado_por_linea(ls)
            for k in range(1, len(ls) - 1):
                if ls[k].strip():
                    continue
                ant, sig = ls[k - 1], ls[k + 1]
                if not (ant.strip() and sig.strip()):
                    continue
                prof, cadena = est[k]
                if cadena:
                    mal("7 blanco espurio", n, f"línea {k + 1}: dentro de una cadena")
                elif prof > 0:
                    mal("7 blanco espurio", n, f"línea {k + 1}: dentro de un paréntesis")
                elif ant.lstrip().startswith("#") and sig.lstrip().startswith("#"):
                    mal("7 blanco espurio", n, f"línea {k + 1}: entre dos comentarios")
                elif ant.rstrip().endswith("\\"):
                    mal("7 blanco espurio", n, f"línea {k + 1}: tras una continuación")
            for k in range(1, len(ls)):
                if ls[k].strip() == "" and ls[k - 1].strip() == "":
                    mal("8 blancos dobles", n, f"línea {k + 1}")
            dentro = set()
            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.Import):
                    for a in nodo.names:
                        dentro.add((a.asname or a.name).split(".")[0])
                elif isinstance(nodo, ast.ImportFrom):
                    for a in nodo.names:
                        dentro.add(a.asname or a.name)
            usados = {x.id for x in ast.walk(arbol) if isinstance(x, ast.Name)}
            for m in MODULOS:
                if m in usados and m not in dentro:
                    mal("10 import", n, f"usa «{m}» y no lo importa")
        else:
            if texto.count("```") % 2:
                mal("12 render", n, "valla ``` sin cerrar")
            if texto.count("**") % 2:
                mal("12 render", n, "negritas ** impares")
            en_valla, i = False, 0
            while i < len(ls):
                l = ls[i]
                if VALLA.match(l):
                    en_valla = not en_valla
                    i += 1
                    continue
                if en_valla:
                    if len(l) > ANCHO_VALLA:
                        mal("16 valla ancha", n, f"línea {i + 1}: {len(l)} caracteres")
                    i += 1
                    continue
                if FILA.match(l):
                    if (not SEPARADORA.match(l) and i + 1 < len(ls)
                            and FILA.match(ls[i + 1])
                            and not SEPARADORA.match(ls[i + 1])
                            and (i == 0 or not FILA.match(ls[i - 1]))):
                        mal("13 tabla", n, f"línea {i + 1}: tabla sin separadora")
                    if (i + 2 < len(ls) and ls[i + 1].strip() == ""
                            and FILA.match(ls[i + 2])):
                        mal("13 tabla", n, f"línea {i + 2}: tabla partida")
                if (l.lstrip().startswith(">") and i + 2 < len(ls)
                        and ls[i + 1].strip() == ""
                        and ls[i + 2].lstrip().startswith(">")):
                    mal("14 cita", n, f"línea {i + 2}: cita partida")
                if (VINETA.match(l) and i + 2 < len(ls)
                        and ls[i + 1].strip() == "" and VINETA.match(ls[i + 2])):
                    mal("15 lista", n, f"línea {i + 2}: lista partida")
                if (l.strip() and i + 2 < len(ls) and ls[i + 1].strip() == ""
                        and ls[i + 2].startswith("  ") and ls[i + 2].strip()
                        and not VINETA.match(ls[i + 2])
                        and (VINETA.match(l) or l.startswith("  "))):
                    mal("15 lista", n, f"línea {i + 2}: viñeta partida")
                i += 1
    return fallos


def contra_original(ruta, original):
    fallos = []
    a = json.load(open(original, encoding="utf-8"))
    b = json.load(open(ruta, encoding="utf-8"))
    if len(a["cells"]) != len(b["cells"]):
        fallos.append(("O celdas", "-", f"{len(a['cells'])} -> {len(b['cells'])}"))
        return fallos
    ca = [c for c in a["cells"] if c["cell_type"] == "code"]
    cb = [c for c in b["cells"] if c["cell_type"] == "code"]
    if [c.get("outputs") for c in ca] != [c.get("outputs") for c in cb]:
        fallos.append(("O salidas", "-", "cambiaron"))
    if [c.get("execution_count") for c in ca] != [c.get("execution_count") for c in cb]:
        fallos.append(("O ejecución", "-", "cambiaron"))
    if a.get("metadata") != b.get("metadata"):
        fallos.append(("O metadatos", "-", "cambiaron"))
    for i, (x, y) in enumerate(zip(ca, cb)):
        try:
            if ast_normalizado("".join(x["source"])) != ast_normalizado("".join(y["source"])):
                fallos.append(("O semántica", f"código {i}", "el AST difiere"))
        except SyntaxError as e:
            fallos.append(("O compila", f"código {i}", str(e)))
    return fallos


def main():
    args = sys.argv[1:]
    contra = None
    if "--contra" in args:
        k = args.index("--contra")
        contra = args[k + 1]
        args = args[:k] + args[k + 2:]
    ficheros = [a for a in args if not a.startswith("--")]
    if not ficheros:
        print(__doc__)
        return 2

    total = 0
    for f in ficheros:
        fallos = revisar(f)
        if contra:
            orig = os.path.join(contra, os.path.basename(f))
            if os.path.exists(orig):
                fallos += contra_original(f, orig)
        total += len(fallos)
        marca = "OK" if not fallos else f"{len(fallos)} FALLOS"
        print(f"  {os.path.basename(f):32} {marca}")
        for prueba, celda, msg in fallos[:12]:
            print(f"      [{prueba}] celda {celda}: {msg}")
        if len(fallos) > 12:
            print(f"      … y {len(fallos) - 12} más")

    print()
    if total == 0:
        print("Las dieciséis pruebas pasan en todos los cuadernos.")
    else:
        print(f"{total} fallos. Ninguno se arregla solo: míralos uno a uno.")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
