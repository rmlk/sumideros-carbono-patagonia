# Sumideros de Carbono — Patagonia Chilena

Sitio educativo e interactivo basado en el proyecto de Ciencias para la Ciudadanía sobre la pérdida de sumideros de carbono en los bosques nativos de la Patagonia chilena.

## Stack
- HTML5 + CSS3 + JavaScript vanilla
- Python + Flask
- Gunicorn para producción
- PostgreSQL en Render para los registros de visitantes
- SQLite solo como fallback local
- Video MP4 y podcast MP3 integrados en `static/media/`

## Ejecutar localmente en Windows
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Abre `http://127.0.0.1:5000`.

Si PowerShell bloquea la activación:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Publicar en GitHub + Render
1. Crea un repositorio nuevo en GitHub.
2. Sube **el contenido de esta carpeta**, no la carpeta contenedora adicional.
3. No subas `.venv/` ni `visitors.db`; están excluidos por `.gitignore`.
4. En Render selecciona **New → Blueprint** y conecta el repositorio.
5. Render detectará `render.yaml` y creará un Web Service Flask y una base PostgreSQL.
6. El servicio usa `pip install -r requirements.txt` y `gunicorn app:app`.
7. Espera el deploy y abre la URL `.onrender.com`.

`DATABASE_URL` y `FLASK_SECRET_KEY` se configuran automáticamente mediante `render.yaml`.

## Base de datos
En Render se usa PostgreSQL. Localmente, si `DATABASE_URL` no existe, Flask usa `visitors.db` con SQLite. El alias de visitante es único sin distinguir mayúsculas/minúsculas, por lo que un mismo alias no puede registrarse dos veces.

## Quiz
El banco contiene preguntas basadas en el documento. Cada partida selecciona exactamente 10 preguntas al azar: 3 iniciales, 4 intermedias y 3 difíciles.

## Multimedia
Los archivos ya están preparados con nombres simples:
- `static/media/video.mp4`
- `static/media/podcast.mp3`

No es necesario copiar archivos multimedia después de clonar el repositorio.

## Salud del servicio
Render puede comprobar `/health`, que devuelve el estado de Flask y de la base de datos.
