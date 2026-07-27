#!/bin/bash
# verificacion.sh — contrasta los datasets generados con LOS números publicados
cd "$(dirname "$0")/datasets" || exit 1
# Locale neutro: en un host en español (es_ES), awk lee "219.90" truncando los
# decimales y sort ordena con cotejo distinto. LC_ALL=C hace los números y el
# orden reproducibles en cualquier idioma (dentro del contenedor ya es así).
export LC_ALL=C
PASS=0; FAIL=0
chk () { # chk "descripcion" esperado obtenido
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); echo "OK   $1 = $3";
  else FAIL=$((FAIL+1)); echo "FALLO $1: esperado [$2] obtenido [$3]"; fi
}

echo "== LAB02: dimensiones =="
chk "wc ventas"   "1000001" "$(wc -l < ventas.csv)"
chk "wc clientes" "100001"  "$(wc -l < clientes.csv)"
chk "wc log"      "500000"  "$(wc -l < access.log)"
echo "== LAB02: suciedad =="
chk "ciudades vacias ,,"   "3030" "$(grep -c ',,' ventas.csv)"
chk "zaragoza minuscula"   "2004" "$(cut -d, -f8 ventas.csv | grep -cx 'zaragoza')"
chk "' Zaragoza' espacio"  "941"  "$(cut -d, -f8 ventas.csv | grep -cx ' Zaragoza')"
chk "precios <= 0"         "465"  "$(awk -F, 'NR>1 && $7<=0' ventas.csv | wc -l)"
chk "clientes distintos"   "99996" "$(cut -d, -f3 ventas.csv | tail -n +2 | sort -u | wc -l)"
echo "== LAB03: categorias (contador de frecuencias) =="
TOP=$(cut -d, -f5 ventas.csv | tail -n +2 | sort | uniq -c | sort -rn | awk '{printf "%s %s·", $1, $2}')
chk "top categorias" "200487 jardin·200210 deporte·200208 hogar·199786 informatica·199309 papeleria·" "$TOP"
echo "== LAB03: facturacion =="
TOT=$(awk -F, 'NR>1 {t += $6*$7; n++} END {printf "%.2f %.2f", t, t/n}' ventas.csv)
chk "total y ticket" "429888864.70 429.89" "$TOT"
CIU=$(awk -F, 'NR>1 {f[$8] += $6*$7} END {for (c in f) printf "%.2f %s\n", f[c], c}' ventas.csv | sort -rn | head -4 | awk '{printf "%d %s·", $1, $2}')
chk "ciudades top4" "145650275 Zaragoza·59872662 Madrid·51325419 Barcelona·42491335 Huesca·" "$CIU"
echo "== LAB03: logs =="
COD=$(awk '{print $9}' access.log | sort | uniq -c | sort -rn | awk '{printf "%s %s·", $1, $2}')
chk "codigos http" "426839 200·49267 404·15607 301·6372 403·1915 500·" "$COD"
chk "peticiones atacante" "42000" "$(grep -c '^185\.220\.101\.34 ' access.log)"
RUT=$(grep '^185\.220\.101\.34 ' access.log | awk '{print $7}' | sort | uniq -c | sort -rn | awk '{printf "%s %s·", $1, $2}')
chk "rutas atacante" "8563 /admin·8476 /wp-login.php·8431 /admin/login·8266 /phpmyadmin·8264 /.env·" "$RUT"
SEG=$(awk '{print $1}' access.log | sort | uniq -c | sort -rn | sed -n '2p' | awk '{print $1, $2}')
chk "2a IP (~520)" "520 83.52.101.7" "$SEG"
L404=$(awk '$9==404 {print $7}' access.log | sort | uniq -c | sort -rn | awk '$1 < 1000' | head -1 | awk '{print $1, $2}')
chk "primer 404 legitimo" "46 /producto/P-0259" "$L404"
H500=$(awk '$9==500 {split($4,a,":"); print a[2]}' access.log | sort | uniq -c | sort -rn | head -3 | awk '{printf "%s %s·", $1, $2}')
chk "horas de los 500" "1609 03·28 15·26 19·" "$H500"
chk "linea canonica del manual" "1" "$(grep -cF '83.52.101.7 - - [12/Feb/2025:18:33:01 +0100] "GET /producto/P-1042 HTTP/1.1" 200 5123' access.log)"
echo "== LAB04: jq =="
chk "length"        "480" "$(jq 'length' productos.json)"
chk "precio > 100"  "280" "$(jq '[.[] | select(.precio > 100)] | length' productos.json)"
chk "sin stock central" "25" "$(jq '[.[] | select(.stock.central == 0)] | length' productos.json)"
chk "sin stock TOTAL (leccion IA)" "11" "$(jq '[.[] | select(.stock.central + .stock.tiendas == 0)] | length' productos.json)"
MED=$(jq -r 'group_by(.categoria) | map([.[0].categoria, (map(.precio)|add/length|round)]) | .[] | @tsv' productos.json | awk '{printf "%s %s·", $1, $2}')
chk "precio medio por categoria" "deporte 124·hogar 179·informatica 760·jardin 168·papeleria 21·" "$MED"
jq -r '["id","nombre","categoria","precio","stock_total"],(.[] | [.id,.nombre,.categoria,.precio,(.stock.central + .stock.tiendas)]) | @csv' productos.json > /tmp/productos.csv
chk "productos.csv lineas" "481" "$(wc -l < /tmp/productos.csv)"
chk "P-1042 canonico" '"P-1042","Portátil 15.6 i5","informatica",219.9,20' "$(grep '^"P-1042"' /tmp/productos.csv)"
echo "== Filas canonicas de ventas.csv =="
chk "fila 1" "1,2025-01-02,84321,P-1042,informatica,2,219.90,Zaragoza,web" "$(sed -n '2p' ventas.csv)"
chk "fila 2" "2,2025-01-02,1294,P-0317,hogar,1,34.50,Huesca,tienda" "$(sed -n '3p' ventas.csv)"
echo "== Clientes ausentes (LEFT JOIN B2) =="
AUS=$(comm -23 <(cut -d, -f1 clientes.csv | tail -n +2 | sort) <(cut -d, -f3 ventas.csv | tail -n +2 | sort -u) | sort -n | tr '\n' ' ')
chk "los 4 ausentes" "1373 28460 55011 93208 " "$AUS"
echo
echo "RESULTADO: $PASS OK · $FAIL FALLOS"
[ $FAIL -eq 0 ]
