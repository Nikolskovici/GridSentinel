"""
GridSentinel — Backend FastAPI
"""

import asyncio
import json
import time
from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from grid_simulator import GridSimulator, ScenarioType
from ai_engine import GridAI

TICK_INTERVAL_SEC = 1.0

simulator             = GridSimulator()
ai_engine             = GridAI()
connected_clients     = set()
tick_count            = 0
last_ai_decision      = None
last_ai_tick          = 0
last_ai_node_analysis = {}


async def broadcast(message: dict):
    if not connected_clients:
        return
    data = json.dumps(message)
    dead = set()
    for ws in connected_clients:
        try:
            await ws.send_text(data)
        except Exception:
            dead.add(ws)
    connected_clients.difference_update(dead)


async def grid_loop():
    global tick_count, last_ai_decision, last_ai_tick, last_ai_node_analysis
    print("[DEBUG] grid_loop pornit")
    while True:
        try:
            tick_count += 1
            snapshot  = simulator.generate()
            snap_dict = asdict(snapshot)

            should_analyze = (
                tick_count - last_ai_tick >= 3
                or snapshot.anomaly_detected
            )

            if should_analyze:
                decision              = ai_engine.analyze(snap_dict)
                node_analysis         = ai_engine.analyze_nodes(snap_dict.get("nodes", []))
                last_ai_decision      = asdict(decision)
                last_ai_node_analysis = node_analysis
                last_ai_tick          = tick_count

            message = {
                "type": "grid_update",
                "tick": tick_count,
                "grid": snap_dict,
                "ai": last_ai_decision or {
                    "status": "normal",
                    "recommendation": "Sistem operational. Monitorizare activa.",
                    "action": None,
                    "action_label": None,
                    "confidence": 1.0,
                },
                "node_analysis": last_ai_node_analysis,
            }

            await broadcast(message)
            await asyncio.sleep(TICK_INTERVAL_SEC)

        except Exception as e:
            print(f"[ERROR] grid_loop: {e}")
            await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(grid_loop())
    yield
    task.cancel()


app = FastAPI(title="GridSentinel", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.add(ws)
    print(f"[+] Client conectat. Total: {len(connected_clients)}")
    try:
        while True:
            raw     = await ws.receive_text()
            command = json.loads(raw)
            await handle_command(command, ws)
    except WebSocketDisconnect:
        connected_clients.discard(ws)
        print(f"[-] Client deconectat. Total: {len(connected_clients)}")
    except Exception as e:
        connected_clients.discard(ws)
        print(f"[!] Eroare: {e}")


async def handle_command(command: dict, ws: WebSocket):
    cmd = command.get("type")
    if cmd == "set_scenario":
        mapping = {
            "normal": ScenarioType.NORMAL,
            "macro":  ScenarioType.MACRO,
            "cyber":  ScenarioType.CYBER,
        }
        s = mapping.get(command.get("scenario"), ScenarioType.NORMAL)
        simulator.set_scenario(s)
        await broadcast({"type": "scenario_changed", "scenario": s.value})
    elif cmd == "approve_action":
        await broadcast({
            "type": "action_executed",
            "action": command.get("action"),
            "message": "Actiune aprobata si executata de operator.",
            "timestamp": time.time(),
        })
    elif cmd == "reject_action":
        await broadcast({
            "type": "action_rejected",
            "message": "Plan respins de operator. Sistem in mod manual.",
            "timestamp": time.time(),
        })
    elif cmd == "ping":
        await ws.send_text(json.dumps({"type": "pong"}))


@app.get("/api/status")
async def status():
    return {
        "running":  True,
        "tick":     tick_count,
        "scenario": simulator.scenario.value,
        "clients":  len(connected_clients),
    }

@app.post("/api/scenario/{scenario}")
async def set_scenario(scenario: str):
    mapping = {"normal": ScenarioType.NORMAL, "macro": ScenarioType.MACRO, "cyber": ScenarioType.CYBER}
    if scenario not in mapping:
        return {"error": "Scenariu invalid"}
    simulator.set_scenario(mapping[scenario])
    return {"ok": True, "scenario": scenario}

# Serveste index.html - trebuie sa fie ultimul mount
app.mount("/", StaticFiles(directory=".", html=True), name="static")

