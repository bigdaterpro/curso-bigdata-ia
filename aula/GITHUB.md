# GITHUB.md — crear el repositorio, actualizarlo por bloques y clonarlo donde toque
Guía del DOCENTE (⌂ siempre en terminal del host). Complementa a ACTUALIZAR.md (el ciclo
entre clases). Aquí: el nacimiento del repo, la publicación por bloques y la clonación.

## 0) Dos decisiones antes de empezar
- **Nombre:** `curso-bigdata-ia` (el que ya usan todos los materiales).
- **Visibilidad: PÚBLICO.** Razones: los datos son sintéticos y ni siquiera viajan (se
  generan), el repo solo lleva activos técnicos (máquinas+datos+labs); la teoría y el vademécum viven en Moodle, fuera del repo, y un repo público se clona en los puestos SIN credenciales — cero fricción de
  aula. Privado obligaría a un token en cada puesto: evitable.

## 1) Preparación de tu máquina (una sola vez)
    sudo apt install -y git                      # si no está (Debian limpia)
    git config --global user.name  "Tu Nombre"
    git config --global user.email "tu@correo"
    git config --global init.defaultBranch main
Cuenta en github.com si no la tienes. Y tu llave para EMPUJAR (clonar no la necesita):
GitHub ya no acepta tu contraseña por git — usa un **token**: github.com → Settings →
Developer settings → Personal access tokens → Tokens (classic) → Generate: marca el
alcance `repo`, caducidad a tu gusto, y GUÁRDALO (se enseña una vez). Cuando git pida
"Password" al hacer push, pegas el TOKEN. El primer uso puede quedar recordado por el
ayudante de credenciales del sistema.

## 2) Crear el repositorio en GitHub (una sola vez)
En github.com: **New repository** → nombre `curso-bigdata-ia` → Public →
**SIN marcar** "Add a README" ni licencia ni .gitignore (tu copia local ya trae todo;
un repo-vacío evita conflictos en el primer push). Copia la URL HTTPS que te da:
`https://github.com/TU_USUARIO/curso-bigdata-ia.git`

## 3) Primera publicación (desde tu copia de trabajo — la del zip r3)
El zip NO trae historial git (no hay carpeta .git): se inaugura aquí.
    cd curso-bigdata-ia
    git init
    git add -A
    git status                                   # revisa: datasets/ NO aparece (.gitignore)
    git commit -m "Bloque 1 · rev.3 — curso completo hasta S3"
    git tag b1-r3
    git remote add origin https://github.com/TU_USUARIO/curso-bigdata-ia.git
    git push -u origin main --tags               # usuario + TOKEN como password
Verificación: recarga la página del repo — ficheros, y en "Tags", b1-r3. Y la prueba de
fuego real: clónalo tú mismo en /tmp y pasa la verificación (paso 5).

## 4) Actualizar en cada bloque (el ciclo de publicación)
Cuando integres el material de un bloque nuevo en tu copia (o edites algo):
    cd curso-bigdata-ia
    git add -A
    git commit -m "Bloque 2 · rev.2 — SQL, JOINs y Spark"
    git tag b2-r2                                # una etiqueta por bloque/revisión
    git push && git push --tags
Las etiquetas del curso: b1-r3 · b2-r2 · b3-r2 (y las que vengan). Sirven de foto fija:
`git checkout b1-r3` reconstruye el curso tal como estaba en el Bloque 1 — tu máquina
del tiempo si algo se tuerce. El lado del ALUMNO entre clases está en ACTUALIZAR.md
(git pull + verificación); esta guía es tu mitad.

## 5) Clonar en una máquina de ejecución (banco, servidor del aula, puesto)
    git clone https://github.com/TU_USUARIO/curso-bigdata-ia.git    # sin credenciales: es público
    cd curso-bigdata-ia
    python3 generar_datasets.py                  # los datos NACEN aquí (no viajaron)
    bash verificacion.sh                         # 28 OK  — y desde el B2: bash verificacion_b2.sh (16 OK)
    docker compose up -d                         # y el entorno, arriba
En el aula, esa URL sustituye al marcador `<URL-del-repositorio-del-curso>` del LAB01
(pizarra y manual del primer día). Nota de víspera: comprueba que la red del centro deja
salir a github.com (está en tu ronda de red); si no, el plan B de siempre — el zip por
http.server o USB — ES el repositorio por otra vía.

## 6) Averías típicas
- push rechazado "fetch first": el repo remoto no estaba vacío (marcaste el README).
  Arreglo limpio: bórralo en GitHub y repite el paso 2 sin README.
- "Authentication failed": pegaste tu contraseña — va el TOKEN.
- token caducado: generar otro; el push te lo pedirá.
- clonaste y verificacion falla: ¿generaste los datasets? (paso 5 — no viajan a propósito).
- pull del alumno con conflicto: ACTUALIZAR.md, sección B (copia → checkout → pull).
