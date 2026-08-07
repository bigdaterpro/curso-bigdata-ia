# PROMPT A · INFORME CON GRÁFICOS DE TEXTO Y TABLAS
## Edición definitiva · universal, con cualquier filtro
**Curso Big Data e IA Aplicada · Formación San Miguel · Zaragoza**

> **Cómo se usa.** Pégalo en la caja de prompt del cuadro de mando. Funciona tal cual, tengas los
> filtros que tengas: **no lleva ni una cifra tuya dentro**.
>
> Sube `CONTEXTO_INFORME_TEXTO.md` a tu asistente si quieres adaptarlo.

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
  3. Un gráfico, si procede (REGLAS DE GRÁFICO)
  4. Su TABLA, siempre que haya gráfico (REGLAS DE TABLA)
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

═══ REGLAS DE GRÁFICO · son aritmética, no estilo ═══

G0. LA VALLA. Todo gráfico va DENTRO de un bloque de código, entre tres
    comillas invertidas. SIEMPRE, y la CABECERA también va dentro. Sin la
    valla, Markdown junta las líneas en un párrafo y las pinta con fuente
    proporcional: el gráfico se destruye.

G1. ESCALA. Antes de dibujar:  escala = valor_máximo / 30
    Decláralo en la cabecera:  [Título · 1 bloque = X,XXX unidad]

G2. LONGITUD. ESCRIBE LA DIVISIÓN, no la calcules de cabeza. Al final de cada
    barra, entre paréntesis:
      (valor / escala = cociente -> bloques redondeados)
    Ejemplo:  (59,9 / 4,897 = 12,23 -> 12)
    Si no escribes la división, te equivocarás en el redondeo.

G3. RELLENO OBLIGATORIO. La barra ocupa SIEMPRE 30 caracteres: los bloques
    llenos con █ y el resto con ·  hasta completar 30. El relleno no es
    adorno: es lo que te permite contar hasta 30 sin perderte.

G4. AVISO ⚠ · ÚSALO POCO. Calcula el desvío:
      desvío % = |bloques x escala - valor| / valor * 100
    Marca la fila con ⚠ SOLO si ese desvío supera el 5 %.
    NO se marca:  20 x 7,143 = 142,86 frente a 143,3  -> 0,3 %  ->  sin ⚠
    SÍ se marca:  11 x 4,897 = 53,87 frente a 59,9    -> 10,1 % ->  con ⚠
    Un aviso que salta siempre deja de avisar. Si te salen más de dos ⚠ en un
    gráfico, es que has redondeado mal: repite la G2.

G4b. EL NÚMERO MANDA SOBRE EL DIBUJO. La barra tiene que llevar EXACTAMENTE
    los bloques que has declarado entre paréntesis. Antes de entregar, repasa
    cada fila y cuéntalos. Si no coinciden, corrige el DIBUJO, nunca el
    número: el número sale de una división y el dibujo, de contar.
    Y usa SOLO dos caracteres: █ para lleno y · para vacío, PEGADOS entre sí.
    Nada de espacios entre bloques, medios bloques, asteriscos ni ningún otro
    invento. Una barra es una línea continua:
      correcto:  [████████··················]
      MAL:       [█ █ █ █ █ █ █ █]

G5. Dos valores distintos NO pueden tener el mismo número de bloques. Si
    ocurre, repite el gráfico con ancho 40 en vez de 30.

G6. Cada gráfico usa SU propia escala y la declara. Nunca invites a comparar
    barras de dos gráficos distintos.

G7. SERIES PLANAS -> NO SE DIBUJAN. Calcula y ESCRIBE la operación:
      dispersión = (máx - mín) / media * 100
    Escríbela con los números:  (36,11 - 35,49) / 35,82 * 100 = 1,73 %
    Si el resultado es MENOR del 5 %, PROHIBIDO el gráfico de barras: saldrían
    todas iguales. En su lugar, SOLO la tabla del apartado T3.

G8. CASOS LÍMITE, sin excepción:
    - una sola categoría            -> sin gráfico, solo tabla
    - todos los valores iguales     -> sin gráfico, y dilo
    - más de 12 categorías          -> las 10 primeras, y avisa de cuántas faltan
    - magnitudes distintas          -> sin gráfico. Euros, operaciones y
                                       personas NO van en el mismo eje

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

T1. TODO GRÁFICO VA SEGUIDO DE SU TABLA, con las cifras exactas. El gráfico
    da la forma; la tabla da el número. Un gráfico que no enseña su tabla es
    una opinión.

T2. La tabla lleva las cifras TAL CUAL vienen del CONTEXTO. No redondees más
    de lo que ya venían. Columnas: la categoría, el valor, y los bloques que
    le has dado.

T3. SERIES PLANAS: tabla con cuatro columnas —periodo, valor, desviación
    sobre la media con su signo, y ▲ o ▼—. Sin barras.

T5. En las tablas se colorea SOLO la columna del valor, y solo las dos filas
    que cumplan un criterio de K3. Nunca la fila entera. Y el símbolo va
    DENTRO del color, igual que en el párrafo:  :green[▲ 214,3]  —nunca
    :green[214,3] a secas—.

T4. Las tablas van en Markdown normal, FUERA de la valla de código.

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

C7. Si un hallazgo no admite gráfico honesto, escribe "Sin gráfico:" seguido
    del motivo, en una línea. Cinco gráficos NO son obligatorios.
```

---

# LO QUE DEBE SALIR · tus anclas de gráfico

Si lo que te devuelve no se parece a esto, no ha cumplido las reglas.

## Comparar categorías

````
```
[Facturación por canal · 1 bloque = 7,143 M€]
tienda : [██████████████████████████████]  214,3 M€  (214,3 / 7,143 = 30,00 -> 30)
web    : [████████████████████··········]  143,3 M€  (143,3 / 7,143 = 20,06 -> 20)
movil  : [██████████····················]   72,3 M€  (72,3 / 7,143 = 10,12 -> 10)
```

| Canal | M€ | Bloques |
|---|---|---|
| tienda | 214,3 | 30 |
| web | 143,3 | 20 |
| movil | 72,3 | 10 |
````

## Un ranking

````
```
[Facturación por ciudad · 1 bloque = 4,897 M€]
Zaragoza  : [██████████████████████████████]  146,9 M€  (146,9 / 4,897 = 30,00 -> 30)
Madrid    : [████████████··················]   59,9 M€  (59,9 / 4,897 = 12,23 -> 12)
Barcelona : [██████████····················]   51,3 M€  (51,3 / 4,897 = 10,48 -> 10)
Huesca    : [█████████·····················]   42,5 M€  (42,5 / 4,897 = 8,68 -> 9)
Valencia  : [██████························]   28,3 M€  (28,3 / 4,897 = 5,78 -> 6)
```
````

> 🎯 **Fíjate en Madrid y en Huesca.** Escribiendo la división salen **12** y **9**. Sin escribirla,
> el modelo pone 11 y 8 — y entonces el desvío se dispara al 10 % y aparece un ⚠ que en realidad
> denuncia su propio redondeo.

## Una serie plana · la regla G7

```
Dispersión = (36,11 − 35,49) / 35,82 × 100 = 1,73 % → menor del 5 %: solo tabla.
```

| Mes | M€ | Desviación | |
|---|---|---|---|
| 2025-01 | 36,00 | +0,18 | ▲ |
| 2025-08 | 35,51 | −0,31 | ▼ |
| 2025-10 | 35,49 | −0,33 | ▼ |
| 2025-12 | 36,11 | +0,29 | ▲ |

> ⚠️ **Por qué una serie plana ya no se dibuja.** Con barras absolutas salen todas iguales. Con
> símbolos, el modelo tiene que elegir una escala y contar hasta doce — y ahí es donde falla: en las
> pruebas se inventó la escala y llegó a mezclar ▲ y ▼ en la misma fila. **La tabla no exige contar
> nada y dice lo mismo con más precisión.**

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
| **0** | !¿Cada gráfico va **dentro de una valla ```**? Si no, no hay gráfico |
| **1** | ¿Declara la **escala** en la cabecera? |
| **2** | ¿Está **escrita la división** en cada barra, y el redondeo es correcto? |
| **3** | ¿Miden **30 caracteres** todas las barras, contando los `·`? |
| **3b** | !¿Los bloques **dibujados** son los **declarados** entre paréntesis? Si no, **manda el número**: la tabla y la división son lo fiable |
| **4** | ¿Hay **pocos ⚠**? Si están casi todos, ha redondeado mal |
| **5** | ¿La serie plana viene **como tabla**, con la dispersión calculada y escrita? |
| **6** | ¿**Toda** tabla acompaña a su gráfico, con las cifras exactas? |
| **7b** | ¿Hay **como mucho tres cifras coloreadas** por hallazgo, y cada color con su criterio escrito? |
| **7c** | ¿Toda cifra coloreada lleva **su símbolo** ▲▼●⚓ delante? |
| **8** | !¿Hay alguna cifra que **no esté en el contexto** ni sea una división escrita? Comprueba los dígitos uno a uno |
| **7** | !¿Declara el filtro **en el título** si las cifras no son las del negocio completo? |

> ⚠️ **Sobre la 3b, con franqueza.** Pintar treinta caracteres idénticos es contar, y un modelo de
> lenguaje no cuenta de forma fiable: en las pruebas acertó todas las divisiones y falló tres de
> ocho dibujos. **Por eso la precisión vive en la tabla y en el paréntesis, no en la barra.** La
> barra da la forma; si baila un bloque, no pasa nada. Si baila un número, sí.

**La 7 es la que más vale.** Un informe con todas las cifras correctas y el alcance sin declarar
hace que quien lo lee se equivoque, y las cifras no le avisan.

---

*Prompt A · edición definitiva · Formación San Miguel · Zaragoza*
