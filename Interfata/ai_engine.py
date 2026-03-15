import sys
import os
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
AI_ENGINE_DIR = ROOT_DIR / 'AI engine'
INTEGRARE_DIR = ROOT_DIR / 'Integrare_AI'
DATA_DIR = ROOT_DIR / 'data'

sys.path.append(str(AI_ENGINE_DIR))
sys.path.append(str(INTEGRARE_DIR))

try:
    import joblib
    import tensorflow as tf
    tf.get_logger().setLevel('ERROR')
    from tensorflow.keras.models import load_model

    MODEL = load_model(AI_ENGINE_DIR / 'model_gridsentinel.keras')
    SCALER = joblib.load(AI_ENGINE_DIR / 'scaler_gridsentinel.pkl')
    ML_AVAILABLE = True
    print("[AI] Model Keras incarcat cu succes!")
except Exception as e:
    ML_AVAILABLE = False
    MODEL = None
    SCALER = None
    print(f"[AI] Model ML indisponibil: {e}")

try:
    possible_csvs = [
        DATA_DIR / 'telemetry_stream.csv',
        DATA_DIR / 'telemetry_live.csv',
        ROOT_DIR / 'telemetry_stream.csv',
        ROOT_DIR / 'telemetry_live.csv',
    ]
    csv_path = next((p for p in possible_csvs if p.exists()), None)
    if csv_path is None:
        raise FileNotFoundError("Nu exista CSV de telemetrie in locatiile asteptate.")

    TELEMETRY_DATA = pd.read_csv(csv_path)
    TELEMETRY_DATA = TELEMETRY_DATA.replace({
        'ON': 1, 'OFF': 0,
        'On': 1, 'Off': 0,
        'on': 1, 'off': 0
    })
    TELEMETRY_DATA = TELEMETRY_DATA.apply(pd.to_numeric, errors='coerce').fillna(0)
    CSV_AVAILABLE = True
    print(f"[AI] CSV incarcat: {len(TELEMETRY_DATA)} inregistrari din {csv_path.name}.")
except Exception as e:
    CSV_AVAILABLE = False
    TELEMETRY_DATA = None
    print(f"[AI] CSV indisponibil: {e}")

from AI_INTEGRATION import CyberGridOptimizer

SEVERITY_COLORS = {
    0: "#3fb950",
    1: "#94d3a2",
    2: "#ffc107",
    3: "#fd7e14",
    4: "#dc3545",
    5: "#000000"
}

COLOANE_INUTILE = ['timestamp', 'nivel_severitate', 'curent_a', 'is_attack', 'label', 'station_id']

NODE_EDGE_MAP = {
    "BUC": ["BUC-PLO", "BUC-BRL", "BUC-CAL", "BUC-CST"],
    "CLJ": ["CLJ-ORD", "CLJ-TGM", "CLJ-SBU", "CLJ-ALB"],
    "CST": ["CST-BRL", "CST-CRN", "CST-TLC", "CST-TRC"],
    "PFR": ["PFR-DRO", "PFR-VID"],
    "VID": ["VID-PIT", "VID-PFR", "VID-SBU"],
    "BCN": ["BCN-SUC", "BCN-IAS"],
    "IAS": ["IAS-SUC", "IAS-BCU"],
    "BRZ": ["BRZ-PLO", "BRZ-TRC"],
    "CRN": ["CRN-CST", "CRN-CAL"],
    "ORD": ["ORD-CLJ", "ORD-BMR", "ORD-TMS"],
    "TGM": ["TGM-CLJ", "TGM-BCU", "TGM-IAS"],
    "PLO": ["PLO-BUC", "PLO-BRZ", "PLO-BCU"],
    "BRL": ["BRL-BUC", "BRL-CST", "BRL-GAL"],
    "SUC": ["SUC-BCN", "SUC-IAS"],
    "TMS": ["TMS-DRO", "TMS-ORD", "TMS-ARD"],
}

CRITICAL_LABELS = {"BUC", "CLJ", "CST", "PFR", "VID", "BCN", "IAS", "CRN"}


@dataclass
class AIDecision:
    status: str
    recommendation: str
    action: str | None
    action_label: str | None
    confidence: float
    severity_level: int = 0
    node_colors: dict = field(default_factory=dict)
    target_node: str | None = None
    cut_edges: list[str] = field(default_factory=list)


class GridAI:
    FREQ_WARN_LOW = 49.85
    FREQ_WARN_HIGH = 50.15
    DEFICIT_CRITICAL = 800

    def __init__(self):
        self._freq_history = []
        self._max_history = 20
        self._optimizer = CyberGridOptimizer()
        self._csv_index = 0
        self._attack_index = 0
        self._normal_index = 0

        if CSV_AVAILABLE and TELEMETRY_DATA is not None and len(TELEMETRY_DATA) > 0:
            if "nivel_severitate" in TELEMETRY_DATA.columns:
                self._attack_rows = TELEMETRY_DATA[TELEMETRY_DATA["nivel_severitate"] >= 3].reset_index(drop=True)
                self._normal_rows = TELEMETRY_DATA[TELEMETRY_DATA["nivel_severitate"] == 0].reset_index(drop=True)
            else:
                self._attack_rows = TELEMETRY_DATA.copy().reset_index(drop=True)
                self._normal_rows = TELEMETRY_DATA.copy().reset_index(drop=True)
        else:
            self._attack_rows = None
            self._normal_rows = None

    def _get_csv_row(self) -> dict:
        if not CSV_AVAILABLE or TELEMETRY_DATA is None or len(TELEMETRY_DATA) == 0:
            return {}

        # alternam intre perioade normale si perioade cu atac,
        # ca UI-ul sa arate schimbari vizibile live
        use_attack = (self._csv_index % 8 in [4, 5, 6])

        if use_attack and self._attack_rows is not None and len(self._attack_rows) > 0:
            row = self._attack_rows.iloc[[self._attack_index % len(self._attack_rows)]]
            self._attack_index += 1
        elif self._normal_rows is not None and len(self._normal_rows) > 0:
            row = self._normal_rows.iloc[[self._normal_index % len(self._normal_rows)]]
            self._normal_index += 1
        else:
            row = TELEMETRY_DATA.iloc[[self._csv_index % len(TELEMETRY_DATA)]]

        self._csv_index += 1

        date = row.drop(columns=[c for c in COLOANE_INUTILE if c in row.columns], errors='ignore')

        deficit = 0.0
        if "flux_intrare_mw" in row.columns and "flux_iesire_mw" in row.columns:
            flux_in = float(row["flux_intrare_mw"].values[0])
            flux_out = float(row["flux_iesire_mw"].values[0])
            deficit = max(0.0, flux_out - flux_in)
        elif "deficit_mw" in row.columns:
            deficit = float(row["deficit_mw"].values[0])

        station_id = row["station_id"].values[0] if "station_id" in row.columns else None
        severity = int(row["nivel_severitate"].values[0]) if "nivel_severitate" in row.columns else 0

        return {
            "data": date,
            "deficit": deficit,
            "station_id": station_id,
            "severity": severity,
        }

    def _predict_anomaly(self, snapshot: dict) -> tuple[float, float, str | None, int]:
        """
        Returneaza:
        - probabilitate cyber
        - deficit estimat
        - station_id suspect din CSV
        - severity din CSV
        """
        if CSV_AVAILABLE and ML_AVAILABLE:
            try:
                csv_row = self._get_csv_row()
                if csv_row:
                    date_scalate = SCALER.transform(csv_row["data"])
                    predictie = MODEL.predict(date_scalate, verbose=0)
                    prob = float(predictie[0][0])

                    severity = int(csv_row.get("severity", 0))
                    if severity >= 5:
                        prob = max(prob, 0.92)
                    elif severity >= 3:
                        prob = max(prob, 0.75)

                    return (
                        prob,
                        float(csv_row["deficit"]),
                        csv_row.get("station_id"),
                        severity
                    )
            except Exception as e:
                print(f"[AI] Eroare CSV predict: {e}")

        if ML_AVAILABLE:
            try:
                freq = snapshot.get("frequency_hz", 50.0)
                nodes = snapshot.get("nodes", [])
                loads = [abs(n.get("load_mw", 0)) for n in nodes if n.get("load_mw", 0) != 0]
                tensiune = 400.0 if not loads else min(400.0, sum(loads) / max(len(loads), 1) * 0.1)
                flux_in = snapshot.get("total_capacity_mw", 14823.0)
                flux_out = snapshot.get("total_demand_mw", 14560.0)

                features = np.array([[1, 0, freq, tensiune, flux_in, flux_out]])
                features_scaled = SCALER.transform(features)
                reconstructed = MODEL.predict(features_scaled, verbose=0)
                mse = float(np.mean((features_scaled - reconstructed) ** 2))
                prob = min(0.99, mse * 1000)
                return prob, float(snapshot.get("deficit_mw", 0.0)), None, 0
            except Exception as e:
                print(f"[AI] Eroare predict: {e}")

        anomaly = snapshot.get("anomaly_type")
        if anomaly == "fdia":
            return 0.85, float(snapshot.get("deficit_mw", 0.0)), None, 5

        return 0.0, float(snapshot.get("deficit_mw", 0.0)), None, 0

    def _choose_suspect_node(self, nodes: list, prob_cyber: float) -> str | None:
        if not nodes:
            return None

        offline_nodes = [n for n in nodes if not n.get("online", True)]
        if offline_nodes:
            offline_nodes.sort(
                key=lambda n: (
                    0 if n.get("label") in CRITICAL_LABELS else 1,
                    -float(n.get("anomaly_score", 0.0)),
                    -abs(float(n.get("load_mw", 0.0)))
                )
            )
            label = offline_nodes[0].get("label")
            if label:
                return label

        scored = [n for n in nodes if n.get("label")]
        if scored:
            scored.sort(
                key=lambda n: (
                    -float(n.get("anomaly_score", 0.0)),
                    0 if n.get("label") in CRITICAL_LABELS else 1,
                    -abs(float(n.get("load_mw", 0.0)))
                )
            )
            best = scored[0]
            best_score = float(best.get("anomaly_score", 0.0))
            if best_score > 0.20 or prob_cyber > 0.55:
                return best.get("label")

        for preferred in ["CLJ", "BUC", "CST", "PFR", "VID", "BCN", "IAS", "CRN"]:
            if any(n.get("label") == preferred for n in nodes):
                return preferred

        return scored[0].get("label") if scored else None

    def _build_cut_edges(self, target_node: str | None, action: str | None) -> list[str]:
        if not target_node or action != "isolate_scada":
            return []
        return NODE_EDGE_MAP.get(target_node, [])

    def analyze(self, snapshot: dict) -> AIDecision:
        freq = float(snapshot.get("frequency_hz", 50.0))
        deficit_snapshot = float(snapshot.get("deficit_mw", 0.0))
        anomaly = snapshot.get("anomaly_type")
        nodes = snapshot.get("nodes", [])

        self._freq_history.append(freq)
        if len(self._freq_history) > self._max_history:
            self._freq_history.pop(0)

        prob_cyber, deficit_csv, csv_station_id, csv_severity = self._predict_anomaly(snapshot)
        deficit = max(deficit_snapshot, deficit_csv)

        nod_suspect = csv_station_id or self._choose_suspect_node(nodes, prob_cyber)

        evaluare = self._optimizer.evalueaza_stare_retea(
            deficit_mw=deficit,
            probabilitate_cyber=prob_cyber,
            nod_suspect=nod_suspect
        )

        nivel = int(evaluare["nivel_severitate"])
        recomandare = evaluare["recomandare_ai"]
        tip_atac = evaluare.get("tip_atac", "Anomalie")

        if prob_cyber >= 0.60 or csv_severity >= 3 or nivel >= 4 or anomaly == "fdia":
            target_node = nod_suspect
            cut_edges = self._build_cut_edges(target_node, "isolate_scada")

            return AIDecision(
                status="critical",
                recommendation=f"ATAC CYBER DETECTAT. {tip_atac}. {recomandare}",
                action="isolate_scada",
                action_label=f"IZOLEAZA {target_node}" if target_node else "IZOLEAZA SCADA",
                confidence=min(max(prob_cyber, 0.70), 0.99),
                severity_level=max(nivel, 4),
                target_node=target_node,
                cut_edges=cut_edges,
            )

        if deficit > self.DEFICIT_CRITICAL or csv_severity >= 3 or nivel >= 3 or anomaly == "physical":
            offline = [n for n in nodes if not n.get("online", True)]
            offline_labels = ", ".join(n["label"] for n in offline if n.get("label")) or "necunoscut"

            return AIDecision(
                status="alert",
                recommendation=f"Deficit critic {deficit:.0f} MW. Noduri offline: {offline_labels}. {recomandare}",
                action="load_shedding",
                action_label="EXECUTA LOAD SHEDDING",
                confidence=min(max(deficit / 1500, 0.60), 0.99),
                severity_level=max(nivel, 3),
                target_node=nod_suspect,
                cut_edges=[],
            )

        if freq < self.FREQ_WARN_LOW or freq > self.FREQ_WARN_HIGH:
            return AIDecision(
                status="alert",
                recommendation=f"Frecventa in afara intervalului normal: {freq:.3f} Hz.",
                action=None,
                action_label=None,
                confidence=0.75,
                severity_level=2,
                target_node=nod_suspect,
                cut_edges=[],
            )

        if nivel >= 1:
            return AIDecision(
                status="alert",
                recommendation=recomandare,
                action=None,
                action_label=None,
                confidence=0.60,
                severity_level=nivel,
                target_node=nod_suspect,
                cut_edges=[],
            )

        return AIDecision(
            status="normal",
            recommendation=f"Retea stabila. Frecventa: {freq:.3f} Hz. Toti consumatorii critici conectati.",
            action=None,
            action_label=None,
            confidence=0.99,
            severity_level=0,
            target_node=None,
            cut_edges=[],
        )

    def analyze_nodes(self, nodes: list) -> dict:
        results = {}

        for node in nodes:
            node_id = node.get("id")
            label = node.get("label")
            online = node.get("online", True)
            anomaly_score = float(node.get("anomaly_score", 0.0))
            load_mw = float(node.get("load_mw", 0.0))

            if not online:
                severity = 5
                status = "critical"
                message = f"Nod {label} OFFLINE."
            elif anomaly_score > 0.8:
                severity = 4
                status = "critical"
                message = f"Anomalie critica pe {label}. Score: {anomaly_score:.2f}."
            elif anomaly_score > 0.6:
                severity = 3
                status = "critical"
                message = f"Risc ridicat pe {label}. Score: {anomaly_score:.2f}."
            elif anomaly_score > 0.4:
                severity = 2
                status = "warning"
                message = f"Alerta pe {label}. Score: {anomaly_score:.2f}."
            elif anomaly_score > 0.2:
                severity = 1
                status = "warning"
                message = f"Atentie pe {label}. Score: {anomaly_score:.2f}."
            else:
                severity = 0
                status = "normal"
                message = f"{label} operational. Load: {abs(load_mw):.0f} MW."

            results[node_id] = {
                "status": status,
                "severity": severity,
                "color": SEVERITY_COLORS[severity],
                "message": message
            }

        return results
