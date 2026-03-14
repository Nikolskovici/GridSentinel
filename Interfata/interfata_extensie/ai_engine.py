import sys
import os
import numpy as np
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'AI engine'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Integrare_AI'))

try:
    import joblib
    from tensorflow.keras.models import load_model
    MODEL = load_model(os.path.join(os.path.dirname(__file__), '..', 'AI engine', 'model_gridsentinel.keras'))
    SCALER = joblib.load(os.path.join(os.path.dirname(__file__), '..', 'AI engine', 'scaler_gridsentinel.pkl'))
    ML_AVAILABLE = True
    print("[AI] Model Keras incarcat cu succes!")
except Exception as e:
    ML_AVAILABLE = False
    print(f"[AI] Model ML indisponibil, folosesc reguli: {e}")

from AI_INTEGRATION import CyberGridOptimizer


@dataclass
class AIDecision:
    status: str
    recommendation: str
    action: str | None
    action_label: str | None
    confidence: float


class GridAI:

    FREQ_WARN_LOW = 49.85
    FREQ_WARN_HIGH = 50.15
    DEFICIT_WARN = 200
    DEFICIT_CRITICAL = 800

    def __init__(self):
        self._freq_history = []
        self._max_history = 20
        self._optimizer = CyberGridOptimizer()

    def _predict_anomaly(self, snapshot: dict) -> float:
        if not ML_AVAILABLE:
            anomaly = snapshot.get("anomaly_type")
            if anomaly == "fdia":
                return 0.85
            return 0.0

        try:
            freq = snapshot.get("frequency_hz", 50.0)
            nodes = snapshot.get("nodes", [])

            loads = [abs(n.get("load_mw", 0)) for n in nodes if n.get("load_mw", 0) != 0]
            tensiune = 400.0 if not loads else min(400.0, sum(loads) / len(loads) * 0.1)

            flux_in = snapshot.get("total_capacity_mw", 14823.0)
            flux_out = snapshot.get("total_demand_mw", 14560.0)
            status = 1
            weather = 0

            features = np.array([[status, weather, freq, tensiune, flux_in, flux_out]])
            features_scaled = SCALER.transform(features)
            reconstructed = MODEL.predict(features_scaled, verbose=0)
            mse = float(np.mean((features_scaled - reconstructed) ** 2))
            probabilitate = min(0.99, mse * 1000)
            return probabilitate
        except Exception as e:
            print(f"[AI] Eroare predictie: {e}")
            return 0.0

    def analyze(self, snapshot: dict) -> AIDecision:
        freq = snapshot.get("frequency_hz", 50.0)
        deficit = snapshot.get("deficit_mw", 0.0)
        anomaly = snapshot.get("anomaly_type")
        nodes = snapshot.get("nodes", [])

        self._freq_history.append(freq)
        if len(self._freq_history) > self._max_history:
            self._freq_history.pop(0)

        prob_cyber = self._predict_anomaly(snapshot)

        anomaly_node = snapshot.get("anomaly_node_id")
        nod_suspect = None
        if anomaly_node is not None:
            matching = [n for n in nodes if n.get("id") == anomaly_node]
            if matching:
                nod_suspect = matching[0].get("label")

        evaluare = self._optimizer.evalueaza_stare_retea(
            deficit_mw=deficit,
            probabilitate_cyber=prob_cyber,
            nod_suspect=nod_suspect
        )

        nivel = evaluare["nivel_severitate"]
        recomandare = evaluare["recomandare_ai"]
        tip_atac = evaluare["tip_atac"]

        if nivel >= 4 or anomaly == "fdia":
            return AIDecision(
                status="critical",
                recommendation=f"ATAC CYBER DETECTAT. {tip_atac}. {recomandare}",
                action="isolate_scada",
                action_label="IZOLEAZA SCADA",
                confidence=prob_cyber,
            )

        if nivel >= 3 or anomaly == "physical" or deficit > self.DEFICIT_CRITICAL:
            offline = [n for n in nodes if not n.get("online", True)]
            offline_labels = ", ".join(n["label"] for n in offline) or "necunoscut"
            return AIDecision(
                status="alert",
                recommendation=f"Deficit critic {deficit:.0f} MW. Noduri offline: {offline_labels}. {recomandare}",
                action="load_shedding",
                action_label="EXECUTA LOAD SHEDDING",
                confidence=deficit / 1500 if deficit / 1500 < 0.99 else 0.99,
            )

        if freq < self.FREQ_WARN_LOW or freq > self.FREQ_WARN_HIGH:
            return AIDecision(
                status="alert",
                recommendation=f"Frecventa in afara intervalului normal: {freq:.3f} Hz. Monitorizez evolutia.",
                action=None,
                action_label=None,
                confidence=0.75,
            )

        if nivel >= 1:
            return AIDecision(
                status="alert",
                recommendation=recomandare,
                action=None,
                action_label=None,
                confidence=0.60,
            )

        return AIDecision(
            status="normal",
            recommendation=f"Retea stabila. Frecventa: {freq:.3f} Hz. Toti consumatorii critici conectati.",
            action=None,
            action_label=None,
            confidence=0.99,
        )

    def analyze_nodes(self, nodes: list) -> dict:
        results = {}
        for node in nodes:
            node_id = node.get("id")
            label = node.get("label")
            online = node.get("online", True)
            anomaly_score = node.get("anomaly_score", 0.0)
            load_mw = node.get("load_mw", 0.0)

            if not online:
                results[node_id] = {
                    "status": "critical",
                    "message": f"Nod {label} OFFLINE. Interventie urgenta necesara."
                }
            elif anomaly_score > 0.7:
                results[node_id] = {
                    "status": "critical",
                    "message": f"Anomalie critica pe {label}. Score: {anomaly_score:.2f}."
                }
            elif anomaly_score > 0.3:
                results[node_id] = {
                    "status": "warning",
                    "message": f"Deviatie detectata pe {label}. Score: {anomaly_score:.2f}."
                }
            else:
                results[node_id] = {
                    "status": "normal",
                    "message": f"{label} operational. Load: {abs(load_mw):.0f} MW."
                }
        return results