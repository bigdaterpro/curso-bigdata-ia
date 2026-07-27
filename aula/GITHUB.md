## 1) Clonar en una máquina de ejecución (banco, servidor del aula, puesto)
    git clone https://github.com/TU_USUARIO/curso-bigdata-ia.git    # sin credenciales: es público
    cd curso-bigdata-ia
    python3 generar_datasets.py                  # los datos NACEN aquí (no viajaron)
    bash verificacion.sh                         # 28 OK  — y desde el B2: bash verificacion_b2.sh (16 OK)
    docker compose up -d                         # y el entorno, arriba
En el aula, esa URL sustituye al marcador `<URL-del-repositorio-del-curso>` del LAB01
(pizarra y manual del primer día). Nota de víspera: comprueba que la red del centro deja
salir a github.com (está en tu ronda de red); si no, el plan B de siempre — el zip por
http.server o USB — ES el repositorio por otra vía.

## 2) Averías típicas
- push rechazado "fetch first": el repo remoto no estaba vacío (marcaste el README).
  Arreglo limpio: bórralo en GitHub y repite el paso 2 sin README.
- "Authentication failed": pegaste tu contraseña — va el TOKEN.
- token caducado: generar otro; el push te lo pedirá.
- clonaste y verificacion falla: ¿generaste los datasets? (paso 5 — no viajan a propósito).
- pull del alumno con conflicto: ACTUALIZAR.md, sección B (copia → checkout → pull).
