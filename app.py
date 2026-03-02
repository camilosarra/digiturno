from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import socketio
import os

# =========================

# Configuración base

# =========================

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
fastapi_app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(**file**))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Servir archivos estáticos (logo)

fastapi_app.mount(
"/static",
StaticFiles(directory=os.path.join(BASE_DIR, "static")),
name="static"
)

# =========================

# Estado en memoria

# =========================

cola_turnos = []
contador_turnos = 0
atendiendo = None

# =========================

# Rutas HTML

# =========================

@fastapi_app.get("/", response_class=HTMLResponse)
async def home(request: Request):
return templates.TemplateResponse("index.html", {"request": request})

@fastapi_app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
return templates.TemplateResponse("index.html", {"request": request})

# =========================

# WebSocket Eventos

# =========================

@sio.event
async def connect(sid, environ):
await enviar_estado(sid)

@sio.event
async def solicitar_turno(sid, data):
global contador_turnos

```
contador_turnos += 1
turno = {
    "id": contador_turnos,
    "nombre": data["nombre"],
    "tema": data["tema"],
    "sid": sid
}
cola_turnos.append(turno)

await sio.emit("turno_asignado", {"id": turno["id"]}, to=sid)
await enviar_estado()
```

@sio.event
async def llamar_turno(sid, turno_id):
global atendiendo

```
turno_llamado = None
for t in cola_turnos:
    if t["id"] == turno_id:
        turno_llamado = t
        break

if turno_llamado:
    atendiendo = turno_llamado["nombre"]
    cola_turnos.remove(turno_llamado)

    # Avisar solo al usuario llamado
    await sio.emit(
        "turno_llamado",
        {"id": turno_llamado["id"]},
        to=turno_llamado["sid"]
    )

await enviar_estado()
```

# =========================

# Enviar estado global

# =========================

async def enviar_estado(sid=None):
data = {
"cola": [
{"id": t["id"], "nombre": t["nombre"], "tema": t["tema"]}
for t in cola_turnos
],
"atendiendo": atendiendo
}

```
if sid:
    await sio.emit("estado", data, to=sid)
else:
    await sio.emit("estado", data)
```

# =========================

# App final ASGI

# =========================

app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)


# =========================

app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
