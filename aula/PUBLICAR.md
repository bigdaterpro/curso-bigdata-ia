# Publicar el curso al alumnado (Git y/o red del aula)

Regla previa e innegociable: **el Vademécum del Docente jamás entra en lo que se publica**
(contiene todas las soluciones). Lo que se comparte es esta carpeta `curso-bigdata-ia/`.

## Opción A — Repositorio Git (GitHub, o Gitea del centro)
```bash
cd curso-bigdata-ia
git init -b main
git add .
git commit -m "Bloque 1 · rev. 3"
git tag b1-r3
git remote add origin <URL-de-tu-repo>
git push -u origin main --tags
```
El alumno clona con `git clone <URL>`. Al inicio de cada bloque: commit nuevo + etiqueta
(`b2-r1`…). El `.gitignore` ya excluye datasets y derivados: el repo pesa < 1 MB.
**Recuerda sustituir el marcador** `<URL-del-repositorio-del-curso>` que usa el LAB01:
escríbela en la pizarra y en el correo de convocatoria.

## Opción B — Red del aula, sin Git
Desde el puesto del docente, en la carpeta que contiene el zip:
```bash
python3 -m http.server 8000
```
El alumno abre `http://IP-DEL-DOCENTE:8000`, descarga `curso-bigdata-ia.zip` y descomprime.
(La IP del docente: `ip a`. Apagar el servidor al terminar: Ctrl+C.)

## Opción C — USB
El zip pesa menos de 1 MB (los datos se generan en cada puesto): cualquier USB vale.
Las **imágenes Docker** son otra historia (~5 GB): van aparte, ver `IMAGENES_USB.md`.
