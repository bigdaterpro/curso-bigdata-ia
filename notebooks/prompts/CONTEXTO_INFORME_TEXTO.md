# CONTEXTO · INFORMES CON GRÁFICOS DE TEXTO
## Documento para tu asistente · súbelo al RAG antes de pedirle nada
**Curso Big Data e IA Aplicada · Formación San Miguel · Zaragoza**

> **Para qué sirve.** Con esto cargado, tu asistente puede **ayudarte a adaptar el prompt** a lo que
> tú quieras: otro número de hallazgos, otro tipo de gráfico, otro tono. Sin esto, te dará reglas
> que suenan bien y producen gráficos falsos.
>
> **Es la ficha de contexto del LAB00 aplicada a la redacción de informes.**

---

# 1 · QUÉ RECIBE EL MODELO

La aplicación le inyecta un JSON con **cifras ya verificadas**. Nunca datos crudos: nunca puede
calcular una suma, solo usar las que se le dan.

```json
{
  "operaciones":       999535,          <- ENTERO: se escribe 999.535, no 999535,0
  "facturacion":       429892547.06,
  "ticket_medio":      430.09,
  "clientes_activos":  99996,
  "por_canal":  [{"canal": "tienda",  "millones": 214.3}, ...],
  "por_ciudad": [{"ciudad": "Zaragoza", "millones": 146.9}, ...],
  "por_mes":    [{"mes": "2025-01", "millones": 36.0}, ...]
}
```

**El contenido cambia con los filtros de la barra lateral.** Por eso el prompt no puede llevar
cifras dentro: tiene que funcionar con cualquier recorte.

---

# 2 · ⚓ LAS ANCLAS · y cómo detectan un filtro

| Sin ningún filtro puesto | Valor |
|---|---|
| Operaciones | **999.535** |
| Facturación | **429.892.547,06 €** |
| Ticket medio | **430,09 €** |
| Clientes activos | **99.996** |
| Canal, en millones | tienda **214,3** · web **143,3** · movil **72,3** |
| Ciudades, en millones | Zaragoza **146,9** · Madrid **59,9** · Barcelona **51,3** · Huesca **42,5** |

> 🎯 **El truco que hace universal al prompt:** el ancla no solo verifica, **detecta**. Si el
> CONTEXTO no trae 999.535 operaciones, hay filtros — y el informe tiene que decirlo en el título.
> Sin esa regla, un informe de tres ciudades se presenta como si fuera todo el negocio y quien lo
> lee se equivoca en cientos de millones, con todas las cifras correctas.

---

# 3 · ⚠️ ANTES DE NADA: LA VALLA

Un gráfico de texto **solo se sostiene con fuente monoespaciada y con los saltos de línea
respetados**. Markdown no hace ninguna de las dos cosas con texto suelto:

| Cómo se entrega | Qué produce | Resultado |
|---|---|---|
| Texto suelto | `<p>línea1 línea2 línea3</p>` | Fuente proporcional, saltos colapsados: **destruido** |
| !Dentro de ``` | `<pre><code>…</code></pre>` | Monoespaciada y con sus saltos: **intacto** |

**Todo gráfico de texto va dentro de un bloque de código.** Vale igual en la caja del cuadro de
mando, en el `.md` descargado y en un cuaderno.

---

# 4 · CÓMO SE CONSTRUYE UNA BARRA HONESTA

Una barra es **aritmética**, no adorno. Tres pasos:

```
1. escala  = valor_máximo / 30
2. bloques = redondeo(valor / escala)
3. relleno = 30 - bloques   (con el carácter ·)
```

Y se escribe la comprobación al lado, para que se pueda auditar de un vistazo:

```
[Facturación por canal · 1 bloque = 7,14 M€]
Tienda : [██████████████████████████████]  214,3 M€  (30 x 7,14 = 214,3)
Web    : [████████████████████··········]  143,3 M€  (20 x 7,14 = 142,9)
Móvil  : [██████████····················]   72,3 M€  (10 x 7,14 = 71,4)
```

## Las series planas NO se dibujan: se tabulan

Calcula y **escribe** la operación:

```
dispersión = (máx − mín) / media × 100 = (36,11 − 35,49) / 35,82 × 100 = 1,73 %
```

Si sale por debajo del 5 %, **las barras absolutas salen todas iguales**. Y los gráficos de símbolos
tampoco valen: obligan al modelo a elegir una escala y contar hasta doce, que es justo donde falla
—en las pruebas se inventó la escala y llegó a mezclar ▲ y ▼ en la misma fila—.

**La tabla no exige contar nada y dice lo mismo con más precisión:**

| Mes | M€ | Desviación | |
|---|---|---|---|
| 2025-01 | 36,00 | +0,18 | ▲ |
| 2025-08 | 35,51 | −0,31 | ▼ |
| 2025-12 | 36,11 | +0,29 | ▲ |

---

# 5 · TODA TABLA ACOMPAÑA A SU GRÁFICO

El gráfico da **la forma**; la tabla da **el número**. Van juntos siempre.

| | |
|---|---|
| El gráfico | Se ve de un vistazo, y es aproximado por definición |
| La tabla | Es exacta, y es lo que se copia a otro sitio |

> 🎯 **«Un gráfico que no enseña su tabla es una opinión.»** Es la regla de oficio de la sesión 10,
> aplicada al informe.

**Y hay un motivo práctico, medido.** Pintar treinta caracteres idénticos es contar, y un modelo de
lenguaje no cuenta de forma fiable: en las pruebas acertó **todas** las divisiones y falló **tres de
ocho** dibujos. La división y la tabla son exactas; la barra es aproximada por naturaleza. **Por eso
van juntas.**

**La tabla va en Markdown normal, fuera de la valla de código.** Dentro de la valla saldría en
crudo, con sus tuberías a la vista.

---

# ⚠️ LA CIFRA CON UN DÍGITO DE MÁS

El fallo más peligroso que hemos visto no fue de formato. En una prueba, el modelo escribió
**999.996 clientes activos** donde el contexto decía **99.996**. Tres veces. Y después calculó un
ratio a partir de esa cifra.

| | |
|---|---|
| Lo que decía el contexto | `"clientes_activos": 99996` |
| Lo que escribió el informe | **999.996** clientes |
| Lo que derivó de ahí | «429,91 € de facturación por cliente» — con el dato bueno son **4.299,10 €** |

**Un dígito de más no chirría.** La cifra sigue teniendo pinta de cifra, el ratio sigue saliendo, y
la frase se lee bien. Nada avisa.

Por eso la regla **C9** obliga a un repaso final: cada cifra del informe, o está literalmente en el
contexto, o es una división escrita al lado. Y por eso, en el aula, **la auditoría contra el ancla
no es un trámite**: es lo único que separa un informe correcto de uno que parece correcto.

---

# EL COLOR · cómo se usa sin que sea adorno

El cuadro de mando entiende la sintaxis de color de **Streamlit**, también dentro de las tablas:

```
:red[texto]   :green[texto]   :orange[texto]   :blue[texto]   :gray[texto]
```

| Color | Símbolo | Qué significa |
|---|---|---|
| Azul | ⚓ | Cifra ancla: los totales del alcance, ya verificados |
| Verde | ▲ | Lidera el grupo o está por encima de la media |
| Rojo | ▼ | Cierra el grupo, está por debajo, o exige acción |
| Naranja | ● | Al límite: menos de un 2 % de diferencia con otra del grupo |
| Sin color | — | Cifra de contexto. **La mayoría van así** |

## Las tres reglas que evitan que se vuelva un adorno

**El símbolo es obligatorio, el color no basta.** Fuera del cuadro de mando —en el `.md`
descargado, en GitHub, en un cuaderno— `:green[▲ 214,3]` se ve en crudo. **El ▲ sobrevive y el
informe se sigue leyendo.** Y hay un motivo más: nadie debería depender del color para entender un
dato.

**Dos o tres en el párrafo, dos filas en la tabla, y la leyenda una sola vez.** Es la misma lección del ⚠: un aviso que salta
siempre deja de avisar. Un informe con todo coloreado es un semáforo averiado.

**El criterio se escribe al lado, con el número.** No *«está en verde»*, sino *«está
:green[▲ 214,3 M€], un 49,9 % del total»*. El color señala; el número justifica.

---

# 6 · LOS ERRORES QUE SE COMETEN QUE SE COMETEN

| Error | Cómo se detecta |
|---|---|
| !**Gráfico sin valla** | Las líneas salen seguidas, como un párrafo. **El más frecuente** |
| !**Todas las barras iguales** | Doce meses con veinte bloques cada uno. La escala está mal o la serie es plana |
| !**Escala sin declarar** | No hay `1 bloque = X` en la cabecera. Entonces no se puede comprobar nada |
| **Escala distinta dentro del mismo gráfico** | `bloques × escala` no da el valor en alguna fila |
| !**El ⚠ en casi todas las filas** | Solo se marca por encima del 5 % de desvío. Si están casi todas, ha redondeado mal |
| !**El redondeo de bloques, a ojo** | Se arregla obligándole a escribir la división: `59,9 / 4,897 = 12,23 -> 12` |
| **Gráfico sin su tabla** | La tabla es donde vive la precisión |
| !**El dibujo no coincide con lo declarado** | Cuenta los bloques de la barra y compáralos con el número entre paréntesis. **Manda el número** |
| **Caracteres inventados** en la barra | Solo `█` y `·`. Nada de asteriscos ni medios bloques |
| **Filas de distinta anchura** | Se cuentan los caracteres entre corchetes: 30 en todas |
| !**Magnitudes mezcladas** | Euros, operaciones y clientes en el mismo eje. No son comparables |
| **Comparar entre gráficos** | Cada gráfico tiene su escala. Dos barras de 30 bloques no valen lo mismo |
| !**Alcance sin declarar** | El título no dice que hay filtros y el informe habla de «el negocio» |
| **Decimales en lo que se cuenta** | «999.535,0 operaciones». Media transacción no existe |
| **Relleno descuadrado** | Filas de distinta anchura. Si no puedes garantizarlo, quita el relleno |

---

# 7 · LO QUE EL MODELO NO SABE, Y HAY QUE DECIRLE

**No sabe qué NO tiene.** No hay costes, ni márgenes, ni campañas, ni stock, ni competencia. Si no
se lo dices, construirá recomendaciones sobre datos que no existen.

**No sabe que los datos son sintéticos.** La regularidad mensual del conjunto es una propiedad del
generador, no del negocio. Un modelo la leerá como un rasgo comercial y recomendará campañas para
romperla.

**Y sobre todo: no sabe qué filtros tienes puestos.** Solo ve las cifras. Por eso la detección por
ancla es obligatoria y no una florituras.

---

# 8 · EL PROMPT QUE LE PASAS PARA ADAPTAR EL TUYO

```
ROL
  Eres experto en comunicación de datos y en diseño de informes ejecutivos.

CONTEXTO
  (adjunta este documento y el PROMPT_A_informe_texto.md)

TAREA
  Adapta el prompt para que <lo que quieras cambiar>, manteniendo intactas
  las reglas de ALCANCE y las reglas G1 a G8.

FORMATO
  El prompt completo, listo para pegar. Sin explicaciones alrededor.

EJEMPLO
  (pega el bloque de reglas de gráfico del prompt A)
```

> ⚠️ **Lo que no se toca:** el ALCANCE y las reglas de gráfico. Ahí es donde está todo lo que hemos
> aprendido a base de informes malos. El resto —número de hallazgos, tono, longitud, idioma— es
> tuyo.

---

*Contexto para informes de texto · Formación San Miguel · Zaragoza*
