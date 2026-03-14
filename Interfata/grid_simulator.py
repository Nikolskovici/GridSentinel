"""
GridSentinel — Generator Date Mock
Simulează datele SCADA ale rețelei electrice naționale.
Folosit de FastAPI pentru a alimenta dashboardul via WebSocket.
"""

import random
import math
import time
from dataclasses import dataclass, asdict
from typing import Literal
from enum import Enum


# ─────────────────────────────────────────
# TIPURI DE DATE
# ─────────────────────────────────────────

class ScenarioType(str, Enum):
    NORMAL = "normal"
    MACRO  = "macro"   # Criză fizică — deficit MW
    CYBER  = "cyber"   # Atac FDIA — frecvență manipulată


@dataclass
class NodeStatus:
    id: int
    label: str
    type: str           # city / nuclear / hydro / thermo
    online: bool
    load_mw: float      # Consum / producție curentă (MW)
    anomaly_score: float  # 0.0 = normal, 1.0 = anomalie maximă


@dataclass
class GridSnapshot:
    timestamp: float
    scenario: str
    frequency_hz: float       # Frecvența rețelei (nominal 50 Hz)
    total_capacity_mw: float  # Capacitate totală disponibilă
    total_demand_mw: float    # Cerere totală
    deficit_mw: float         # Deficit (0 = OK)
    nodes: list               # Lista NodeStatus
    anomaly_detected: bool
    anomaly_type: str | None  # None / "physical" / "fdia"
    anomaly_node_id: int | None
    alert_message: str | None


# ─────────────────────────────────────────
# DEFINIȚIE NODURI
# ─────────────────────────────────────────

NODES_DEF = [
    {"id": 0,  "label": "BUC", "type": "city",    "base_demand": 1850},
    {"id": 1,  "label": "CLJ", "type": "city",    "base_demand": 420},
    {"id": 2,  "label": "SUC", "type": "city",    "base_demand": 180},
    {"id": 3,  "label": "CST", "type": "city",    "base_demand": 380},
    {"id": 4,  "label": "TMS", "type": "city",    "base_demand": 390},
    {"id": 5,  "label": "PLO", "type": "city",    "base_demand": 320},
    {"id": 6,  "label": "CRV", "type": "city",    "base_demand": 210},
    {"id": 7,  "label": "BRL", "type": "city",    "base_demand": 190},
    {"id": 8,  "label": "BIS", "type": "city",    "base_demand": 120},
    {"id": 9,  "label": "ORD", "type": "city",    "base_demand": 200},
    {"id": 10, "label": "PIT", "type": "city",    "base_demand": 240},
    {"id": 11, "label": "BCU", "type": "city",    "base_demand": 230},
    {"id": 12, "label": "SLT", "type": "city",    "base_demand": 110},
    {"id": 13, "label": "DRO", "type": "city",    "base_demand": 160},
    {"id": 14, "label": "CAL", "type": "city",    "base_demand": 90},
    {"id": 15, "label": "GAL", "type": "city",    "base_demand": 220},
    {"id": 16, "label": "SBU", "type": "city",    "base_demand": 170},
    {"id": 17, "label": "TGM", "type": "city",    "base_demand": 200},
    {"id": 18, "label": "CRN", "type": "nuclear", "base_demand": -1400},  # producer
    {"id": 19, "label": "PFR", "type": "hydro",   "base_demand": -800},
    {"id": 20, "label": "VID", "type": "hydro",   "base_demand": -300},
    {"id": 21, "label": "BCN", "type": "hydro",   "base_demand": -200},
    {"id": 22, "label": "BRZ", "type": "thermo",  "base_demand": -600},
    {"id": 23, "label": "ISN", "type": "thermo",  "base_demand": -500},
    {"id": 24, "label": "TRC", "type": "thermo",  "base_demand": -400},
]

TOTAL_CAPACITY_MW = 14823.0
TOTAL_DEMAND_MW   = 14560.0


# ─────────────────────────────────────────
# GENERATOR PRINCIPAL
# ─────────────────────────────────────────

class GridSimulator:
    def __init__(self):
        self.scenario: ScenarioType = ScenarioType.NORMAL
        self._tick = 0
        self._cyber_phase = 0.0

    def set_scenario(self, scenario: ScenarioType):
        self.scenario = scenario
        self._tick = 0
        self._cyber_phase = 0.0

    def generate(self) -> GridSnapshot:
        self._tick += 1
        t = time.time()

        if self.scenario == ScenarioType.NORMAL:
            return self._normal(t)
        elif self.scenario == ScenarioType.MACRO:
            return self._macro(t)
        else:
            return self._cyber(t)

    # ── Scenariu normal ──────────────────
    def _normal(self, t: float) -> GridSnapshot:
        freq = 50.0 + random.gauss(0, 0.015)
        nodes = self._base_nodes(all_online=True, noise=0.05)
        return GridSnapshot(
            timestamp=t,
            scenario="normal",
            frequency_hz=round(freq, 4),
            total_capacity_mw=TOTAL_CAPACITY_MW,
            total_demand_mw=TOTAL_DEMAND_MW,
            deficit_mw=0.0,
            nodes=[asdict(n) for n in nodes],
            anomaly_detected=False,
            anomaly_type=None,
            anomaly_node_id=None,
            alert_message=None,
        )

    # ── Scenariu criză fizică ────────────
    def _macro(self, t: float) -> GridSnapshot:
        # Cernavodă (id=18) offline → pierdere 1400 MW
        freq = 49.72 + random.gauss(0, 0.05)
        deficit = 1400.0 + random.gauss(0, 30)
        capacity = TOTAL_CAPACITY_MW - deficit

        nodes = self._base_nodes(all_online=True, noise=0.08)
        # Cernavodă offline
        for n in nodes:
            if n.id == 18:
                n.online = False
                n.load_mw = 0.0
                n.anomaly_score = 1.0

        return GridSnapshot(
            timestamp=t,
            scenario="macro",
            frequency_hz=round(freq, 4),
            total_capacity_mw=round(capacity, 1),
            total_demand_mw=TOTAL_DEMAND_MW,
            deficit_mw=round(deficit, 1),
            nodes=[asdict(n) for n in nodes],
            anomaly_detected=True,
            anomaly_type="physical",
            anomaly_node_id=18,
            alert_message=f"Centrala Cernavodă offline. Deficit {deficit:.0f} MW. Frecvență: {freq:.3f} Hz.",
        )

    # ── Scenariu atac cyber FDIA ─────────
    def _cyber(self, t: float) -> GridSnapshot:
        # Frecvența oscilează ritmic artificial — semnătură FDIA
        self._cyber_phase += 0.08
        fdia_signal = math.sin(self._cyber_phase) * 0.20
        freq = 50.0 + fdia_signal + random.gauss(0, 0.01)

        nodes = self._base_nodes(all_online=True, noise=0.03)
        # Constanța (id=3) — senzori compromisi
        for n in nodes:
            if n.id == 3:
                n.anomaly_score = min(1.0, abs(fdia_signal) * 4 + 0.5)

        return GridSnapshot(
            timestamp=t,
            scenario="cyber",
            frequency_hz=round(freq, 4),
            total_capacity_mw=TOTAL_CAPACITY_MW,
            total_demand_mw=TOTAL_DEMAND_MW,
            deficit_mw=0.0,
            nodes=[asdict(n) for n in nodes],
            anomaly_detected=True,
            anomaly_type="fdia",
            anomaly_node_id=3,
            alert_message=f"Oscilație artificială detectată: {freq:.4f} Hz. Pattern FDIA pe stația Constanța.",
        )

    # ── Helper noduri ────────────────────
    def _base_nodes(self, all_online: bool, noise: float) -> list[NodeStatus]:
        nodes = []
        for n in NODES_DEF:
            base = n["base_demand"]
            load = base * (1 + random.uniform(-noise, noise))
            nodes.append(NodeStatus(
                id=n["id"],
                label=n["label"],
                type=n["type"],
                online=all_online,
                load_mw=round(load, 1),
                anomaly_score=round(random.uniform(0, 0.05), 3),
            ))
        return nodes


# ─────────────────────────────────────────
# TEST RAPID
# ─────────────────────────────────────────

if __name__ == "__main__":
    import json

    sim = GridSimulator()

    print("=== NORMAL ===")
    snap = sim.generate()
    print(f"Frecvență: {snap.frequency_hz} Hz | Deficit: {snap.deficit_mw} MW")

    print("\n=== CRIZĂ FIZICĂ ===")
    sim.set_scenario(ScenarioType.MACRO)
    snap = sim.generate()
    print(f"Frecvență: {snap.frequency_hz} Hz | Deficit: {snap.deficit_mw} MW")
    print(f"Alertă: {snap.alert_message}")

    print("\n=== ATAC CYBER ===")
    sim.set_scenario(ScenarioType.CYBER)
    for i in range(5):
        snap = sim.generate()
        print(f"Tick {i+1}: {snap.frequency_hz} Hz | Anomalie: {snap.anomaly_score if hasattr(snap, 'anomaly_score') else 'N/A'}")

    print("\nSimulator OK.")