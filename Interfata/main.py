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


def enrich_ai_decision(decision_dict: dict, snap_dict: dict) -> dict:
    if not decision_dict:
        return {
            "status": "normal",
            "recommendation": "Sistem operational. Monitorizare activa.",
            "action": None,
            "action_label": None,
            "confidence": 1.0,
            "target_node": None,
            "cut_edges": [],
        }

    decision_dict.setdefault("target_node", None)
    decision_dict.setdefault("cut_edges", [])

    nod_afectat = decision_dict.get("nod_afectat")
    if nod_afectat and not decision_dict.get("target_node"):
        decision_dict["target_node"] = nod_afectat

    if decision_dict.get("target_node") is None:
        anomaly_node_id = snap_dict.get("anomaly_node_id")
        nodes = snap_dict.get("nodes", [])
        if anomaly_node_id is not None and 0 <= anomaly_node_id < len(nodes):
            node = nodes[anomaly_node_id]
            label = node.get("label") or node.get("name")
            if label:
                decision_dict["target_node"] = label

    muchii = decision_dict.get("muchii_de_taiat")
    if muchii and isinstance(muchii, list) and not decision_dict.get("cut_edges"):
        decision_dict["cut_edges"] = muchii

    target = decision_dict.get("target_node")
    action = decision_dict.get("action")

    if action == "isolate_scada" and target and not decision_dict.get("cut_edges"):
        demo_edges = {
            "CLJ": ["CLJ-ORD", "CLJ-TGM", "CLJ-SBU"],
            "BUC": ["BUC-PLO", "BUC-BRL", "BUC-CST"],
            "CST": ["CST-BRL", "CST-CRN", "CST-TLC"],
            "PFR": ["PFR-DRO", "PFR-VID"],
            "VID": ["VID-PIT", "VID-PFR", "VID-SBU"],
            "BCN": ["BCN-SUC", "BCN-IAS"],
            "IAS": ["IAS-SUC", "IAS-BCU"],
            "BRZ": ["BRZ-PLO", "BRZ-TRC"],
            "CRN": ["CRN-CST", "CRN-CAL"],
        }
        decision_dict["cut_edges"] = demo_edges.get(target, [])

    return decision_dict


def apply_ai_result_to_snapshot(snap_dict: dict, ai_dict: dict) -> dict:
    if not ai_dict:
        return snap_dict

    target = ai_dict.get("target_node")
    action = ai_dict.get("action")

    if target:
        for i, node in enumerate(snap_dict.get("nodes", [])):
            if node.get("label") == target:
                snap_dict["anomaly_node_id"] = i
                break

    if action == "isolate_scada":
        snap_dict["anomaly_detected"] = True
        snap_dict["anomaly_type"] = "fdia"
        snap_dict["alert_message"] = ai_dict.get("recommendation", "Atac cyber detectat.")
        snap_dict["scenario"] = "cyber"
    elif action == "load_shedding":
        snap_dict["anomaly_detected"] = True
        snap_dict["anomaly_type"] = "physical"
        snap_dict["alert_message"] = ai_dict.get("recommendation", "Dezechilibru energetic detectat.")
        snap_dict["scenario"] = "macro"
    else:
        snap_dict["alert_message"] = ai_dict.get("recommendation", "")
        if ai_dict.get("status") == "normal":
            snap_dict["anomaly_detected"] = False
            snap_dict["anomaly_type"] = None
            snap_dict["anomaly_node_id"] = None
            snap_dict["scenario"] = "normal"

    return snap_dict


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
            snapshot = simulator.generate()
            snap_dict = asdict(snapshot)

            should_analyze = True

            if should_analyze:
                decision = ai_engine.analyze(snap_dict)
                node_analysis = ai_engine.analyze_nodes(snap_dict.get("nodes", []))

                raw_decision = asdict(decision)
                last_ai_decision = enrich_ai_decision(raw_decision, snap_dict)

                print("[AI DEBUG]", last_ai_decision)

                last_ai_node_analysis = node_analysis
                last_ai_tick = tick_count

            if last_ai_decision:
                snap_dict = apply_ai_result_to_snapshot(snap_dict, last_ai_decision)

            print("[GRID DEBUG]", {
                "scenario": snap_dict.get("scenario"),
                "anomaly_type": snap_dict.get("anomaly_type"),
                "anomaly_node_id": snap_dict.get("anomaly_node_id"),
                "alert_message": snap_dict.get("alert_message"),
            })

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
                    "target_node": None,
                    "cut_edges": [],
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
            raw = await ws.receive_text()
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
            "macro": ScenarioType.MACRO,
            "cyber": ScenarioType.CYBER,
        }
        s = mapping.get(command.get("scenario"), ScenarioType.NORMAL)
        simulator.set_scenario(s)

        await broadcast({
            "type": "scenario_changed",
            "scenario": s.value
        })

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
        "running": True,
        "tick": tick_count,
        "scenario": simulator.scenario.value,
        "clients": len(connected_clients),
    }


@app.post("/api/scenario/{scenario}")
async def set_scenario(scenario: str):
    mapping = {
        "normal": ScenarioType.NORMAL,
        "macro": ScenarioType.MACRO,
        "cyber": ScenarioType.CYBER
    }

    if scenario not in mapping:
        return {"error": "Scenariu invalid"}

    simulator.set_scenario(mapping[scenario])
    return {"ok": True, "scenario": scenario}


app.mount("/", StaticFiles(directory=".", html=True), name="static")
