#!/bin/bash
# verificacion_b2.sh — contrasta los datos con los números publicados del BLOQUE 2.
# Se verifica CON la herramienta del bloque (DuckDB vía Python), igual que el B1
# se verificaba con la suya (shell). Requiere: pip install duckdb
# La vista ventas_limpio de aquí ES la definición canónica LIMPIO-v1 del curso.
# NOTA rev.2: el manual escribe TRIM(ciudad)='' ; se usa COALESCE(TRIM(ciudad),'')=''
# porque un campo vacío de CSV llega como NULL y TRIM(NULL) NO es ''. Mismos 16 números.
cd "$(dirname "$0")/datasets" || exit 1
export LC_ALL=C
python3 - <<'PY'
import duckdb, sys
con = duckdb.connect()
# ===================== DEFINICIÓN CANÓNICA · LIMPIO-v1 =====================
con.sql("""CREATE VIEW ventas_limpio AS
SELECT id_venta, fecha, id_cliente, id_producto, categoria, unidades, precio_unitario,
       CASE WHEN COALESCE(TRIM(ciudad),'')='' THEN NULL
            ELSE UPPER(SUBSTR(TRIM(ciudad),1,1)) || LOWER(SUBSTR(TRIM(ciudad),2)) END AS ciudad,
       canal
FROM 'ventas.csv' WHERE precio_unitario > 0""")
con.sql("""CREATE VIEW productos AS
SELECT id, nombre, categoria, precio, stock.central + stock.tiendas AS stock_total
FROM read_json('productos.json')""")
P=F=0
def chk(n, exp, got):
    global P,F
    ok = str(exp)==str(got); P+=ok; F+=not ok
    print(("OK  " if ok else "FALLO")+f" {n} = {got}" + ("" if ok else f"  (esperado {exp})"))
q1 = lambda s: con.sql(s).fetchone()[0]
qa = lambda s: con.sql(s).fetchall()
print("== LIMPIO-v1 ==")
chk("filas limpias", 999535, q1("SELECT COUNT(*) FROM ventas_limpio"))
chk("facturacion limpia", "429892547.06", q1("SELECT ROUND(SUM(unidades*precio_unitario),2) FROM ventas_limpio"))
chk("ticket limpio", "430.09", q1("SELECT ROUND(SUM(unidades*precio_unitario)/COUNT(*),2) FROM ventas_limpio"))
chk("ciudades NULL (eran ',,')", 3030, q1("SELECT COUNT(*) FROM ventas_limpio WHERE ciudad IS NULL"))
chk("Zaragoza tras normalizar", 340693, q1("SELECT COUNT(*) FROM ventas_limpio WHERE ciudad='Zaragoza'"))
print("== LAB06: canal y fechas ==")
chk("canal", "[('tienda', 499184), ('web', 333243), ('movil', 167108)]",
    qa("SELECT canal, COUNT(*) FROM ventas_limpio GROUP BY canal ORDER BY 2 DESC"))
chk("web desde noviembre", 55553, q1("SELECT COUNT(*) FROM ventas_limpio WHERE canal='web' AND fecha>=DATE '2025-11-01'"))
chk("mes pico (M EUR)", "('2025-12', 36.1)", qa("SELECT STRFTIME(fecha,'%Y-%m') m, ROUND(SUM(unidades*precio_unitario)/1e6,1) FROM ventas_limpio GROUP BY m ORDER BY 2 DESC LIMIT 1")[0])
print("== LAB07: JOINs ==")
chk("los 4 ausentes (id,nombre)", "[(1373, 'Ivan', 'Jimenez'), (28460, 'Emma', 'Iglesias'), (55011, 'Hugo', 'Rubio'), (93208, 'Mario', 'Serrano')]",
    qa("SELECT c.id_cliente, c.nombre, c.apellido FROM 'clientes.csv' c LEFT JOIN 'ventas.csv' v USING(id_cliente) WHERE v.id_venta IS NULL ORDER BY 1"))
chk("segmentos de clientes", "[('particular', 60116), ('empresa', 19951), ('premium', 19933)]",
    qa("SELECT segmento, COUNT(*) FROM 'clientes.csv' GROUP BY segmento ORDER BY 2 DESC"))
chk("facturacion por segmento (M, ops)", "[('particular', 258.7, 601073), ('premium', 85.7, 199473), ('empresa', 85.5, 198989)]",
    qa("SELECT c.segmento, ROUND(SUM(v.unidades*v.precio_unitario)/1e6,1), COUNT(*) FROM ventas_limpio v JOIN 'clientes.csv' c USING(id_cliente) GROUP BY 1 ORDER BY 2 DESC"))
chk("clientes activos", 99996, q1("SELECT COUNT(DISTINCT id_cliente) FROM ventas_limpio"))
print("== LAB08: KPIs ==")
chk("top4 ciudades por facturacion", "[('Zaragoza', 146920182.71), ('Madrid', 59873119.57), ('Barcelona', 51325765.64), ('Huesca', 42491623.3)]",
    qa("SELECT ciudad, ROUND(SUM(unidades*precio_unitario),2) FROM ventas_limpio WHERE ciudad IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 4"))
chk("facturacion por canal (M)", "[('tienda', 214.3), ('web', 143.3), ('movil', 72.3)]",
    qa("SELECT canal, ROUND(SUM(unidades*precio_unitario)/1e6,1) FROM ventas_limpio GROUP BY 1 ORDER BY 2 DESC"))
chk("top3 productos por facturacion (M)", "[('Monitor 27 QHD Compact', 14.54), ('Switch 8 puertos Compact', 10.9), ('NAS 2 bahías i5', 10.32)]",
    qa("SELECT p.nombre, ROUND(SUM(v.unidades*v.precio_unitario)/1e6,2) FROM ventas_limpio v JOIN productos p ON v.id_producto=p.id GROUP BY 1 ORDER BY 2 DESC LIMIT 3"))
print("== LAB09/10: los numeros que Spark debe reproducir ==")
chk("categorias limpio (M)", "[('jardin', 58.79), ('deporte', 43.55), ('informatica', 256.5), ('hogar', 61.8), ('papeleria', 9.26)]",
    qa("SELECT categoria, ROUND(SUM(unidades*precio_unitario)/1e6,2) FROM ventas_limpio GROUP BY categoria ORDER BY categoria='jardin' DESC, categoria='deporte' DESC, categoria='informatica' DESC, categoria='hogar' DESC, categoria='papeleria' DESC"))
print(f"\nRESULTADO B2: {P} OK · {F} FALLOS"); sys.exit(1 if F else 0)
PY
