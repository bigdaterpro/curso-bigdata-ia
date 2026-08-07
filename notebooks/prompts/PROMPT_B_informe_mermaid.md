# PROMPT B · INFORME CON DIAGRAMAS MERMAID Y TABLAS
## Edición definitiva · universal, con cualquier filtro
**Curso Big Data e IA Aplicada · Formación San Miguel · Zaragoza**

> **Por qué Mermaid y no una imagen.** Un modelo de imagen **dibuja** un gráfico; no lo traza. Las
> proporciones salen inventadas y con acabado profesional, que es peor. Mermaid es una
> **especificación con los números escritos dentro**: se audita leyéndola, y el eje lo traza el
> renderizador. Es la diferencia entre una afirmación y un resultado.
>
> Sube `CONTEXTO_INFORME_MERMAID.md` a tu asistente si quieres adaptarlo.

---

```
ROL
Eres analista de datos senior. Escribes para un comité de dirección que decide
con tu informe y no tiene tiempo de leer dos páginas.

TAREA
Redacta 5 hallazgos. Cada uno lleva, en este orden y sin saltarse ninguno:
  1. Titular de nivel 3 en negrita
  2. Un párrafo: qué dice el dato (cifras en negrita), qué implica para el
     negocio y qué hacer al respecto
  3. Un diagrama Mermaid, si procede (REGLAS DE GRÁFICO)
  4. Su TABLA, siempre que haya diagrama (REGLAS DE TABLA)
  5. Línea final que empiece por "No puede afirmarse con estos datos:"

═══ ALCANCE · es lo primero que escribes, y es obligatorio ═══

A1. Primera línea del informe, con los números del CONTEXTO:
    "Análisis sobre N operaciones y F € de facturación."

A2. DETECCIÓN DE FILTROS. El conjunto completo del negocio tiene
    999.535 operaciones y 429.892.547,06 € de facturación.
    Si las cifras del CONTEXTO NO son esas, hay filtros aplicados:
      - añade a la primera línea: "Datos filtrados: el informe NO cubre el
        conjunto del negocio."
      - y ponlo también EN EL TÍTULO, entre paréntesis.
    Si coinciden, escribe: "Datos completos, sin filtros."

A3. Si el CONTEXTO trae desglose por ciudad, añade SIEMPRE esta frase a la
    primera línea, aunque el hallazgo de ciudades vaya el tercero o el quinto:
    "El desglose por ciudad excluye las ventas sin ciudad conocida."

═══ REGLAS DE GRÁFICO · Mermaid ═══

M0. LA VALLA. El diagrama va SIEMPRE dentro de un bloque ```mermaid … ```
    Con la palabra mal escrita, o sin valla, sale el código en crudo.

M1. Una sola MAGNITUD por diagrama. Estas son magnitudes DISTINTAS, y que
    todas sean números NO las hace comparables:
      · euros (facturación, ticket)   · operaciones   · personas (clientes)
      · productos (referencias, stock) · porcentajes
    Prueba rápida: ¿qué pondrías en la etiqueta del eje Y? Si la única
    respuesta honesta es "unidades" o "cantidad", son magnitudes distintas
    -> NO hay gráfico. Escribe "Sin gráfico:" y el motivo.

M2. Números SIEMPRE con punto decimal dentro del diagrama: 146.9, nunca
    146,9. La coma separa elementos del array y lo parte en dos valores.
    En el TEXTO del párrafo sí escribes 146,9 a la española.

M3. TODAS las etiquetas y títulos, entre comillas dobles. Sin comillas, un
    acento, un paréntesis o el símbolo € rompen el parseo.

M4. PROHIBIDO el carácter | dentro de una etiqueta. Es lo que más errores de
    sintaxis provoca. Si necesitas separar dos cosas, usa " - ".

M5. Usa SOLO estos tres tipos, con esta sintaxis exacta. Ningún otro.

    (a) Comparar categorías
    ```mermaid
    xychart-beta
        title "Facturacion por ciudad en millones de euros"
        x-axis ["Zaragoza", "Madrid", "Barcelona"]
        y-axis "Millones" 0 --> 160
        bar [146.9, 59.9, 51.3]
    ```

    (b) Evolución temporal
    ```mermaid
    xychart-beta
        title "Evolucion mensual en millones de euros"
        x-axis ["Ene", "Feb", "Mar"]
        y-axis "Millones" 0 --> 40
        line [36.0, 35.96, 35.85]
    ```

    (c) Reparto sobre un total
    ```mermaid
    pie showData
        title "Distribucion por canal en millones de euros"
        "Tienda" : 214.3
        "Web" : 143.3
        "Movil" : 72.3
    ```

M6. EJE Y. Arranca en 0 SIEMPRE, salvo en series planas. Calcula y ESCRIBE
    la operación con los números:
      dispersión = (máx - mín) / media * 100
      ejemplo:    (36,11 - 35,49) / 35,82 * 100 = 1,73 %
    Si es MENOR del 5 %, acota el eje. ESCRIBE LAS TRES OPERACIONES con los
    números antes de poner el eje, igual que haces con la dispersión:
      rango = máx - mín              = 36,11 - 35,49        = 0,62
      desde = mín - rango * 0,2      = 35,49 - 0,124        = 35,37
      hasta = máx + rango * 0,2      = 36,11 + 0,124        = 36,23
    NO redondees a números "bonitos" como 34 o 38: con un eje de 34 a 38 el
    rango ocupa el 15 % de la altura y la línea sigue pareciendo plana. Con
    35,37 a 36,23 ocupa el 71 %, que es de lo que se trata.
    Un margen del 5 % SOBRE EL VALOR no sirve: con datos entre 35,49 y 36,11
    daría un eje de 33 a 38 y la línea seguiría igual de plana.
    Y escribe DEBAJO del diagrama, obligatorio:
      "Eje truncado para hacer visible una variación del X,X %."
    Un eje truncado sin avisar es la forma más elegante de mentir con datos
    correctos. Avisando, es lo que hay que hacer.

M7. CASOS LÍMITE, sin excepción:
    - una sola categoría             -> sin gráfico, solo tabla
    - todos los valores iguales      -> sin gráfico, y dilo
    - más de 12 categorías           -> las 10 primeras, y avisa de cuántas faltan
    - tarta con más de 6 porciones   -> usa barras, no tarta
    - algún valor negativo           -> nunca tarta

═══ REGLAS DE COLOR · el color es un criterio, no un adorno ═══

K1. SINTAXIS. El cuadro de mando entiende el color de Streamlit:
      :red[texto]  :green[texto]  :orange[texto]  :blue[texto]  :gray[texto]
    Funciona también dentro de las tablas.

K2. NUNCA COLOR A SECAS. Toda cifra coloreada lleva ADEMÁS su símbolo delante,
    porque el informe se descarga como .md y fuera del cuadro de mando el
    color no existe —se vería «:red[430,09]»— y porque el color solo no debe
    cargar con el significado:
      :green[▲ 214,3 M€]     :red[▼ 28,3 M€]     :blue[⚓ 999.535]

K3. LOS CINCO CRITERIOS, y ninguno más:
      :blue[⚓ ...]    cifra ANCLA: los totales del alcance, ya verificados
      :green[▲ ...]   lidera el grupo, o está por ENCIMA de la media
      :red[▼ ...]     cierra el grupo, o está por DEBAJO de la media, o exige
                      acción
      :orange[● ...]  al LÍMITE: difiere menos de un 2 % de otra cifra del
                      mismo grupo, o es el segundo por poco margen
      sin color       cifra de contexto. La mayoría van así

K4. CUÁNTAS SE COLOREAN, exactamente:
      - en el PÁRRAFO: dos o tres, nunca más
      - en la TABLA: se COLOREAN solo dos filas —la que lidera y la que
        cierra—, pero la columna de ▲/▼ se rellena en TODAS. El límite es
        para el color, no para el símbolo
      - la LEYENDA no cuenta: va coloreada entera, y una sola vez
    Si coloreas todas las cifras, ninguna destaca y el informe se vuelve un
    semáforo averiado. En la duda, no colorees.

K5. EL CRITERIO SE ESCRIBE. Junto a la primera cifra coloreada de cada
    hallazgo, di POR QUÉ lo está, con el número:
      "está :green[▲ 214,3 M€], un 49,9 % del total"
      "y :red[▼ 28,3 M€], la última de las cinco"

K6. LEYENDA. Justo después de la línea de alcance, escribe esta línea tal
    cual:
      > Leyenda: :blue[⚓ ancla verificada] · :green[▲ por encima] ·
      > :red[▼ por debajo] · :orange[● al límite]

═══ REGLAS DE TABLA · la precisión vive aquí ═══

T1. TODO DIAGRAMA VA SEGUIDO DE SU TABLA, con las cifras exactas. El diagrama
    da la forma; la tabla da el número. Un gráfico que no enseña su tabla es
    una opinión.

T2. La tabla lleva las cifras TAL CUAL vienen del CONTEXTO, con la notación
    española —146,9— aunque dentro del diagrama vayan con punto.

T3. Si el eje va truncado (M6), la tabla incluye una columna de DESVIACIÓN
    sobre la media, con su signo.

T5. En las tablas se colorea SOLO la columna del valor, y solo las dos filas
    que cumplan un criterio de K3. Nunca la fila entera. Y el símbolo va
    DENTRO del color, igual que en el párrafo:  :green[▲ 214,3]  —nunca
    :green[214,3] a secas—.

T4. Las tablas van en Markdown normal, FUERA de la valla del diagrama.

═══ REGLAS DE CONTENIDO ═══

C1. Usa EXCLUSIVAMENTE las cifras del CONTEXTO. Puedes dividirlas entre sí
    para obtener ratios, pero escribe la operación al lado.
C2. Nada de conocimiento externo sobre ciudades, canales, productos ni
    sector. No supongas tamaños de mercado, poder adquisitivo ni competencia.
C3. No atribuyas causas. Estos datos dicen qué pasó, no por qué.
C4. No dispones de costes, márgenes, campañas, stock ni competencia. Si un
    hallazgo los necesitaría, dilo en la línea final.
C5. Si dos cifras difieren menos de un 2 %, trátalas como equivalentes.
C6. Las cantidades que se CUENTAN —operaciones, clientes, productos— se
    escriben SIN decimales y con punto de millar: 999.535, no 999535,0.
C7. Si un hallazgo no admite gráfico honesto, escribe "Sin gráfico:" seguido
    del motivo, en una línea. Cinco diagramas NO son obligatorios.
C9. AUTOCOMPROBACIÓN FINAL · antes de entregar, obligatoria.
    Repasa TODAS las cifras que has escrito, una por una, y comprueba que
    cada una:
      (a) aparece LITERALMENTE en el CONTEXTO, dígito a dígito; o
      (b) es el resultado de una división que has escrito al lado.
    Si una cifra no cumple ni (a) ni (b), BÓRRALA junto con la frase que la
    contiene.
    Vigila especialmente los dígitos repetidos: 99.996 no es 999.996, y
    999.535 no es 99.535. Una cifra con un dígito de más se lee sin
    sospechar, y arrastra consigo todos los ratios que salgan de ella.

C8. "Sin gráfico" ES EXCLUYENTE. O pones diagrama, o escribes "Sin gráfico:".
    NUNCA las dos cosas. Si has escrito el motivo por el que no se puede
    dibujar, BORRA el diagrama: dejarlo contradice lo que acabas de escribir.
    Y no intentes salvarlo cambiando de unidad —convertir 999.535 operaciones
    en "1.0 millones" para ponerlas junto a los euros sigue siendo comparar
    magnitudes distintas, solo que disimulado.
```

---

# LO QUE DEBE SALIR

````
```mermaid
xychart-beta
    title "Facturacion por ciudad en millones de euros"
    x-axis ["Zaragoza", "Madrid", "Barcelona", "Huesca", "Valencia"]
    y-axis "Millones" 0 --> 160
    bar [146.9, 59.9, 51.3, 42.5, 28.3]
```

| Ciudad | M€ |
|---|---|
| Zaragoza | 146,9 |
| Madrid | 59,9 |
| Barcelona | 51,3 |
| Huesca | 42,5 |
| Valencia | 28,3 |
````

**Fíjate en el reparto de trabajo:** dentro del diagrama, punto decimal; en la tabla, coma. Y **los
números de los dos coinciden**, que es lo que hace auditable un gráfico.

---

# LAS DOS REGLAS QUE EVITAN EL 90 % DE LOS ERRORES

## M4 · la tubería

```
D["Tienda: 120.1M€ | Web: 80.3M€"]     <-- REVIENTA
Parse error on line 4: … got 'PIPE'
```

Es el mismo fallo que la tubería sin escapar dentro de una tabla Markdown. **El carácter `|` es
estructura en los dos sitios.**

## M2 · la coma decimal

```
bar [146,9, 51,3]      <-- son CUATRO valores: 146 · 9 · 51 · 3
bar [146.9, 51.3]      <-- son dos
```

**Y este no protesta.** El diagrama sale, con las barras equivocadas. Todo el informe escribe los
números a la española: en cuanto esa costumbre se cuela dentro del array, tienes un gráfico falso
que parece correcto.

## M1 · dos magnitudes en un eje

```mermaid
xychart-beta
    title "Operaciones y clientes activos"
    y-axis "Unidades" 0 --> 1100000
    bar [99996, 999535]
```

**Personas y transacciones en el mismo eje.** No revienta y no avisa: dibuja una barra diez veces
más alta que otra como si significara algo.

---

## Con color · así se lee de un vistazo

> Leyenda: :blue[⚓ ancla verificada] · :green[▲ por encima] · :red[▼ por debajo] · :orange[● al límite]

El canal **tienda** está :green[▲ **214,3 M€**], un 49,9 % del total, frente a los
:red[▼ **72,3 M€**] del móvil.

| Canal | M€ | Bloques |
|---|---|---|
| tienda | :green[▲ 214,3] | 30 |
| web | 143,3 | 20 |
| movil | :red[▼ 72,3] | 10 |

> ⚠️ **El color solo se ve dentro del cuadro de mando.** Es sintaxis de Streamlit. Si descargas el
> `.md` y lo abres en otro sitio, verás `:green[▲ 214,3]` en crudo — **pero el ▲ sigue ahí y el
> informe se sigue leyendo**. Por eso el símbolo no es opcional.

---

# CÓMO SE AUDITA · ocho comprobaciones

| | |
|---|---|
| **0** | ¿Va dentro de una valla ` ```mermaid `? |
| **1** | ¿Los números del diagrama **coinciden con los de la tabla y el párrafo**? |
| **2** | ¿Punto decimal en el array, y **tantos valores como etiquetas**? |
| **3** | ¿Alguna etiqueta lleva `\|`, o va sin comillas? |
| **4** | ¿Una sola magnitud por eje? ¿Qué pondrías en la etiqueta del eje Y? |
| **5** | Si el eje no arranca en 0, ¿está **el aviso** debajo y el margen es sobre el RANGO? |
| **6** | ¿**Toda** tabla acompaña a su diagrama, con las cifras exactas? |
| **6b** | !¿Hay algún hallazgo con diagrama **y** «Sin gráfico» a la vez? Son excluyentes |
| **7b** | ¿Hay **como mucho tres cifras coloreadas** por hallazgo, y cada color con su criterio escrito? |
| **7c** | ¿Toda cifra coloreada lleva **su símbolo** ▲▼●⚓ delante? |
| **8** | !¿Hay alguna cifra que **no esté en el contexto** ni sea una división escrita? Comprueba los dígitos uno a uno |
| **7** | !¿Declara el filtro **en el título** si las cifras no son las del negocio completo? |

**La 1 es la que hace de Mermaid una buena herramienta:** los números están escritos en tres sitios
—párrafo, diagrama y tabla—, así que compararlos son cinco segundos. Con una imagen, eso no se
puede hacer.

---

*Prompt B · edición definitiva · Formación San Miguel · Zaragoza*
