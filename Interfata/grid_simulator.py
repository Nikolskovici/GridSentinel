import random
import math
import time
from dataclasses import dataclass, asdict
from enum import Enum


class ScenarioType(str, Enum):
    NORMAL = "normal"
    MACRO  = "macro"
    CYBER  = "cyber"


@dataclass
class NodeStatus:
    id: int
    label: str
    type: str
    online: bool
    load_mw: float
    anomaly_score: float


@dataclass
class GridSnapshot:
    timestamp: float
    scenario: str
    frequency_hz: float
    total_capacity_mw: float
    total_demand_mw: float
    deficit_mw: float
    nodes: list
    anomaly_detected: bool
    anomaly_type: str | None
    anomaly_node_id: int | None
    alert_message: str | None


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
    {"id": 18, "label": "CRN", "type": "nuclear", "base_demand": -1400},
    {"id": 19, "label": "PFR", "type": "hydro",   "base_demand": -800},
    {"id": 20, "label": "VID", "type": "hydro",   "base_demand": -300},
    {"id": 21, "label": "BCN", "type": "hydro",   "base_demand": -200},
    {"id": 22, "label": "BRZ", "type": "thermo",  "base_demand": -600},
    {"id": 23, "label": "ISN", "type": "thermo",  "base_demand": -500},
    {"id": 24, "label": "TRC", "type": "thermo",  "base_demand": -400},
    {"id": 25, "label": "ARD", "type": "city",    "base_demand": 210},
    {"id": 26, "label": "IAS", "type": "city",    "base_demand": 340},
    {"id": 27, "label": "BMR", "type": "city",    "base_demand": 140},
    {"id": 28, "label": "ALB", "type": "city",    "base_demand": 150},
    {"id": 29, "label": "TLC", "type": "city",    "base_demand": 120},
    {"id": 30, "label": "TGJ", "type": "city",    "base_demand": 170},
]

TOTAL_CAPACITY_MW = 14823.0
TOTAL_DEMAND_MW   = 14560.0
CITY_NODE_IDS     = [n["id"] for n in NODES_DEF if n["type"] == "city"]
PRODUCER_NODE_IDS = [n["id"] for n in NODES_DEF if n["type"] in ("nuclear", "hydro", "thermo")]


class GridSimulator:
    def __init__(self):
        self.scenario: ScenarioType = ScenarioType.NORMAL
        self._tick = 0
        self._cyber_phase = 0.0
        self._cyber_target = None
        self._macro_target = None

    def set_scenario(self, scenario: ScenarioType):
        self.scenario = scenario
        self._tick = 0
        self._cyber_phase = 0.0
        self._cyber_target = None
        self._macro_target = None

    def generate(self) -> GridSnapshot:
        self._tick += 1
        t = time.time()
        if self.scenario == ScenarioType.NORMAL:
            return self._normal(t)
        elif self.scenario == ScenarioType.MACRO:
            return self._macro(t)
        else:
            return self._cyber(t)

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

    def _macro(self, t: float) -> GridSnapshot:
        if self._macro_target is None:
            self._macro_target = random.choice(PRODUCER_NODE_IDS)

        offline_id = self._macro_target
        offline_node = next(n for n in NODES_DEF if n["id"] == offline_id)
        deficit = abs(offline_node["base_demand"]) + random.gauss(0, 30)
        freq = 49.72 + random.gauss(0, 0.05)
        capacity = TOTAL_CAPACITY_MW - deficit

        nodes = self._base_nodes(all_online=True, noise=0.08)
        for n in nodes:
            if n.id == offline_id:
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
            anomaly_node_id=offline_id,
            alert_message=f"Centrala {offline_node['label']} offline. Deficit {deficit:.0f} MW. Frecventa: {freq:.3f} Hz.",
        )

    def _cyber(self, t: float) -> GridSnapshot:
        if self._cyber_target is None:
            self._cyber_target = random.choice(CITY_NODE_IDS)

        self._cyber_phase += 0.08
        fdia_signal = math.sin(self._cyber_phase) * 0.20
        freq = 50.0 + fdia_signal + random.gauss(0, 0.01)

        nodes = self._base_nodes(all_online=True, noise=0.03)
        target_label = None
        for n in nodes:
            if n.id == self._cyber_target:
                n.anomaly_score = min(1.0, abs(fdia_signal) * 4 + 0.5)
                target_label = n.label

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
            anomaly_node_id=self._cyber_target,
            alert_message=f"Oscilatie artificiala detectata: {freq:.4f} Hz. Pattern FDIA pe statia {target_label}.",
        )

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