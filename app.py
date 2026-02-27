from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import socketio

# Socket.IO
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# FastAPI app
fastapi_app = FastAPI()
templates = Jinja2Templates(directory="templates")

# =========================
# Estado en memoria
# =========================
turno_actual = 0
cola_turnos = []
contador_turnos = 0


@fastapi_app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@fastapi_app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "admin": True})


@sio.event
async def connect(sid, environ):
    await enviar_estado(sid)


@sio.event
async def solicitar_turno(sid):
    global contador_turnos
    contador_turnos += 1
    cola_turnos.append(contador_turnos)
    await sio.emit("turno_asignado", {"turno": contador_turnos}, to=sid)
    await enviar_estado()


@sio.event
async def siguiente_turno(sid):
    global turno_actual
    if cola_turnos:
        turno_actual = cola_turnos.pop(0)
    await sio.emit("turno_llamado", {"turno": turno_actual})
    await enviar_estado()


@sio.event
async def marcar_atendido(sid):
    global turno_actual
    turno_actual = 0
    await enviar_estado()


async def enviar_estado(sid=None):
    data = {
        "turno_actual": turno_actual,
        "en_espera": len(cola_turnos),
        "cola": cola_turnos
    }
    if sid:
        await sio.emit("estado", data, to=sid)
    else:
        await sio.emit("estado", data)


# 🔥 ESTA ES LA LÍNEA CORRECTA FINAL
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
