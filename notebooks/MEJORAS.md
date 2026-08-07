# LAS TRES MEJORAS · elige UNA
## El cierre del curso: tú decides qué le falta a la aplicación, y se lo añades
**Formación San Miguel · Big Data e IA Aplicada · Edición Técnica**

> La aplicación funciona. Lo que le falta lo decides tú.
>
> **Eliges una de las tres, se la pides a tu IA con `REFERENCIA_APP.md` como contexto, y la
> auditas.** No se trata de que la IA escriba código: se trata de que **tú sepas si lo que ha
> escrito sirve**. Eso es lo que se puntúa.

---

# CÓMO SE HACE · el protocolo, otra vez

| | |
|---|---|
| **1** | Elige una mejora y **escribe su criterio de éxito ANTES** de pedir nada |
| **2** | Monta el prompt de cinco piezas. Adjunta `REFERENCIA_APP.md` y `app.py` |
| **3** | **Ejecuta lo que te dé TAL CUAL.** Sin arreglarle nada primero |
| **4** | Contrasta contra el ancla de tu mejora |
| **5** | Si falla, **no lo borres**: busca la decisión que tomó por ti, reformula y repite |

> ⚠️ **El paso 3 es el que se salta todo el mundo.** Si le arreglas la ruta o el alias antes de
> probarlo, has destruido la prueba: ya no sabes en qué se equivocaba.

---

# ⓵ ROTACIÓN Y COBERTURA DE STOCK · ¿cuánto dura lo que más se vende?
### Dificultad: media · JOIN + una división con trampa

Una pantalla que cruce **ventas con catálogo** y responda a lo que pregunta un jefe de almacén:
*¿cuántas veces se renueva el almacén, y cuántos días aguanta lo que más se vende?*

**Qué tiene que salir**

| Columna | Cómo |
|---|---|
| Producto y categoría | de `productos` |
| Unidades vendidas | `SUM(v.unidades)` en el periodo filtrado |
| Stock total | `stock_total` (central + tiendas, ya sumado en la vista) |
| **Rotación** | `unidades vendidas / stock_total` — veces que se renueva |
| **Días de cobertura** | `stock_total × días del periodo / unidades vendidas` |
| Un semáforo | y **tres estados distintos**: sin stock, sin ventas, y por días |

**Ancla de control**

> Sin filtros, el producto que más factura es el **Monitor 27 QHD Compact**, con **14,54 M€**.
> Si tu tabla lo pone el primero por facturación, el JOIN está bien hecho.

**⚠️ La trampa · y es la lección de esta mejora**

`stock_total` es **una foto**: lo que hay en el almacén hoy. Las unidades vendidas son **un flujo**:
lo que salió durante todo el periodo. **Dividir una foto entre un flujo anual da siempre "menos de
un mes"** — para el catálogo entero.

Compruébalo tú: el stock medio ronda las **47 unidades** y las ventas medias los **4.000 al año**.
Si mides en meses obtendrás **cuatro valores distintos para casi quinientos productos**, y un
semáforo con todo en rojo.

> 🎯 **Un indicador que da lo mismo para todo no es un indicador.** Si te pasa, no lo maquilles:
> escribe por qué pasa y cambia de métrica. En días se distingue algo; la **rotación** ordena el
> catálogo de verdad.

**⚓ Un control que tienes que ponerle a tu propia pantalla**

Cuenta las filas de tu tabla y compáralas con los productos del catálogo:

```sql
SELECT COUNT(*) FROM productos
```

**Si te salen menos filas que productos, tu `GROUP BY` está fundiendo dos en uno.** Y no da ningún
error: las ventas de los dos aparecen sumadas en una sola línea. Piensa qué columna identifica un
producto y cuál solo lo describe.

> 🎯 Es el **COUNT antes y después** del LAB07, aplicado a una pantalla en vez de a un JOIN.

**El detalle que separa el aprobado del notable**

Tres situaciones que **no son la misma** y que un solo semáforo esconde:

| | |
|---|---|
| **Stock 0** | No es cobertura infinita: es una **rotura**. División entre cero |
| **Ventas 0** | No es stock de sobra: es un producto que **no se vende** |
| **Cobertura baja** | Es lo único que el semáforo debería estar midiendo |

Si las mezclas, las roturas de stock desaparecen entre los críticos y nadie las ve.

---

# ⓶ EVOLUCIÓN POR SEGMENTO · ¿quién tira del mes bueno?
### Dificultad: media-alta · JOIN con clientes + gráfico de varias series

La evolución mensual del Resumen es una sola línea. **Ábrela en tres**: una por segmento de
cliente.

**Qué tiene que salir**

Una línea por `segmento` sobre el mismo eje de meses, con su leyenda. En Plotly es el argumento
`color=`:

```python
px.line(d, x="mes", y="millones", color="segmento", markers=True)
```

**Ancla de control**

> Sin filtros, las operaciones de los tres segmentos suman **999.535** — el cuadre del LAB07.
> Si tu gráfico se construye sobre una suma que no da eso, **el JOIN está multiplicando filas**.

**El detalle que separa el aprobado del notable**

> El segmento está en `clientes`, no en `ventas_limpio`: hace falta un `JOIN` **y el filtro
> cualificado con `donde(filtro, "v")`**. Es exactamente el fallo del que avisa la referencia.
> Y una pregunta para el informe: ¿el mes pico lo es **para los tres segmentos**, o solo para uno?

---

# ⓷ DESCARGAR LO QUE ESTOY VIENDO
### Dificultad: baja de código, alta de criterio · un botón y una decisión

Un botón que exporte a CSV **exactamente las ventas que el filtro deja pasar** — para llevárselas
a otra herramienta, que es lo que pasa en una empresa el día después.

**Qué tiene que salir**

```python
st.download_button("Descargar estas ventas", d.to_csv(index=False),
                   file_name="ventas_filtradas.csv", mime="text/csv")
```

**Ancla de control**

> **El fichero descargado tiene que tener las mismas filas que dice el marcador de la pantalla.**
> Ábrelo y cuéntalas. Si no coinciden, estás exportando otra cosa — casi seguro las 500 de la
> tabla, no las del filtro.

**El detalle que separa el aprobado del notable**

> La pantalla de Ventas enseña **500 filas**, pero el filtro puede dejar pasar cientos de miles.
> ¿Exportas lo que se ve o lo que se ha filtrado? **Las dos respuestas son defendibles; lo que no
> es defendible es no saber cuál has hecho.** Escríbelo en el botón o al lado.
>
> Y la segunda: un CSV con 800.000 filas en el navegador **no es gratis**. ¿Pones un tope? ¿Avisas?

---

# 🏁 Y EL RETO, aparte de la mejora · `RETO`
## Todo tu almacén en Parquet

Tu aplicación lee tres cosas en tres formatos: ventas en **Parquet**, clientes en **CSV**,
productos en **JSON**. Funciona, pero es el desorden con el que empezó el curso.

**Está en el Paso 6 del cuaderno, con sus celdas.** Conviertes clientes, productos y los tres KPI,
mides cuánto se gana, compruebas que no has perdido nada… **y recargas la aplicación sin tocar una
línea de código**: la barra lateral dirá «Clientes: Parquet · Productos: Parquet» ella sola.

**El hallazgo que hay que buscar:** los KPI en Parquet ocupan **MÁS** que en CSV. Tres filas no
amortizan la cabecera del formato. **Un formato no es mejor: es mejor PARA algo** — y eso solo se
sabe midiendo.

---

# CÓMO SE PUNTÚA · 20 puntos

| Pieza | Qué se busca | Pts |
|---|---|---|
| **El criterio, escrito ANTES** | Qué ibas a comprobar, antes de ver el código | 3 |
| **El prompt** | Las cinco piezas identificables, con la referencia adjunta | 3 |
| !**La mejora funciona** | La pantalla se abre y hace lo que dice | 5 |
| !**La verificación contra el ancla** | El número contrastado, **y nombrado** | 5 |
| **La auditoría escrita** | Qué se equivocó la IA, o por qué crees que acertó | 4 |

**La auditoría, con la escala de siempre:**

| | Pts |
|---|---|
| «Funcionó a la primera» y nada más | **1** |
| Dice qué falló y cómo lo arregló | **3** |
| !Identifica **la decisión que el modelo tomó por ti** y la explica | **4** |

> 🎯 **Si te funcionó a la primera, no te quedes ahí.** Escribe **qué parte del contexto se lo
> puso fácil**: ¿la referencia? ¿el ejemplo? ¿el nombre de las columnas? Eso es lo que se
> transfiere al siguiente problema, y puntúa igual.

---

# LO QUE SE ENTREGA

```
[ ] El criterio de exito, escrito ANTES de pedir nada
[ ] El prompt que usaste, entero
[ ] app.py con tu mejora dentro, funcionando
[ ] Una captura de tu pantalla nueva
[ ] El numero del ancla, contrastado
[ ] La auditoria: que decidio la IA por ti
```

> **Y la frase que preside la corrección, por última vez:** una mejora modesta con su verificación
> honesta puntúa por encima de una ambiciosa sin contrastar. Es lo que vale en una empresa.

---

*Las tres mejoras · Formación San Miguel · Zaragoza*
