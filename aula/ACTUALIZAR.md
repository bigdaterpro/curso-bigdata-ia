# ACTUALIZAR.md — cómo evoluciona el repositorio entre clases
El curso es UN repositorio que crece por bloques. El docente publica; el alumnado sincroniza
al empezar la primera sesión de cada bloque (ritual de apertura: pull + verificación).

## A) El DOCENTE publica una actualización (⌂ su máquina)
    cd curso-bigdata-ia
    git add -A
    git commit -m "Bloque 2: cuadernos por sesión, verificacion_b2, docs"
    git tag b2-r1                      # una etiqueta por bloque/revisión: b1-r3, b2-r1...
    git push && git push --tags
Si el aula trabaja SIN remoto git (red local): regenerar el zip y publicarlo por la vía del
LAB01 (servidor http del aula o USB). El zip ES el repositorio: ambas vías son equivalentes.

## B) El ALUMNO sincroniza (⌂ host, dentro de la carpeta del curso)
### Vía git (la buena)
    cd curso-bigdata-ia
    git pull                           # trae cuadernos y docs nuevos
    bash verificacion_b2.sh            # 16 OK = tus datos están alineados con el bloque
Los datasets NO viajan por git (se generan): si verificacion falla o es un puesto nuevo,
`python3 generar_datasets.py` primero.

### ¿git pull protesta por "cambios locales"?
Es la regla de oro del curso trabajando: **los originales del curso se copian antes de
editarse** (tu bitácora y tus copias `mi_*.ipynb` jamás chocan). Si editaste un original:
    cp notebooks/lab06_lab07.ipynb notebooks/mi_lab06_salvado.ipynb   # salva tu trabajo
    git checkout -- notebooks/                                  # restaura los originales
    git pull                                                    # ahora entra limpio

### Vía zip (sin git)
Descarga el zip nuevo, descomprímelo EN OTRA carpeta y copia encima SOLO lo nuevo
(notebooks/, verificacion_b2.sh, aula/, plantillas/). Tus datasets y tus
cuadernos propios no se tocan.

## C) Qué NO hace falta tocar al actualizar
- Contenedores: siguen siendo los mismos (docker compose ni se entera).
- Datasets: idénticos entre bloques (misma semilla). Solo regenerar si verificación falla.
- Tus instalaciones (duckdb, jq): viven en el contenedor; recuerda que un down/up las borra.
