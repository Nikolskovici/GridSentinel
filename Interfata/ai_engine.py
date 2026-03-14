"""
GridSentinel — Motor Decizional AI
Logică Python pură, fără API-uri externe.
Analizează datele rețelei și returnează decizii.
"""

from dataclasses import dataclass


@dataclass
class AIDecision:
    status: str          # "normal" | "alert" | "critical"
    recommendation: str  # Text afișat operatorului
    action: str | None   # None | "load_shedding" | "isolate_scada"
    action_label: str | None
    confidence: float    # 0.0 - 1.0


class GridAI:
    """
    Motor decizional bazat pe reguli și praguri.
    Înlocuiește cu modelul vostru ML când e gata.
    """

    # ── Praguri frecvență ──
    FREQ_NOMINAL       = 50.0
    FREQ_WARN_LOW      = 49.85   # sub acest prag → avertizare
    FREQ_CRITICAL_LOW  = 49.70   # sub acest prag → criză fizică
    FREQ_WARN_HIGH     = 50.15
    FREQ_OSCILLATION_THRESHOLD = 0.10  # amplitudine oscilație FDIA

    # ── Praguri deficit ──
    DEFICIT_WARN     = 200    # MW
    DEFICIT_CRITICAL = 800    # MW

    def __init__(self):
        self._freq_history = []
        self._max_history  = 20

    def analyze(self, snapshot: dict) -> AIDecision:
        """
        Primește un GridSnapshot ca dict și returnează o decizie.
        Aceasta e funcția pe care o înlocuiți cu modelul vostru.
        """
        freq    = snapshot.get("frequency_hz", 50.0)
        deficit = snapshot.get("deficit_mw", 0.0)
        anomaly = snapshot.get("anomaly_type")
        nodes   = snapshot.get("nodes", [])

        # Actualizează istoricul frecvenței
        self._freq_history.append(freq)
        if len(self._freq_history) > self._max_history:
            self._freq_history.pop(0)

        # ── Detecție FDIA (oscilație ritmică) ──
        if anomaly == "fdia" or self._detect_oscillation():
            return AIDecision(
                status="critical",
                recommendation=(
                    f"Oscilație artificială detectată: {freq:.3f} Hz. "
                    "Pattern FDIA confirmat pe stația Constanța. "
                    "NU tăiați curentul — izolați SCADA."
                ),
                action="isolate_scada",
                action_label="IZOLEAZĂ SCADA CONSTANȚA",
                confidence=self._oscillation_confidence(),
            )

        # ── Detecție criză fizică ──
        if anomaly == "physical" or deficit > self.DEFICIT_CRITICAL:
            offline = [n for n in nodes if not n.get("online", True)]
            offline_labels = ", ".join(n["label"] for n in offline) or "necunoscut"
            return AIDecision(
                status="alert",
                recommendation=(
                    f"Deficit critic {deficit:.0f} MW. "
                    f"Noduri offline: {offline_labels}. "
                    "Propun Load Shedding: deconectare consumatori non-critici."
                ),
                action="load_shedding",
                action_label="EXECUTĂ LOAD SHEDDING",
                confidence=min(0.99, deficit / 1500),
            )

        # ── Avertizare frecvență ──
        if freq < self.FREQ_WARN_LOW or freq > self.FREQ_WARN_HIGH:
            return AIDecision(
                status="alert",
                recommendation=(
                    f"Frecvență în afara intervalului normal: {freq:.3f} Hz. "
                    "Monitorizez evoluția. Fără acțiune imediată necesară."
                ),
                action=None,
                action_label=None,
                confidence=0.75,
            )

        # ── Avertizare deficit mic ──
        if deficit > self.DEFICIT_WARN:
            return AIDecision(
                status="alert",
                recommendation=(
                    f"Deficit minor de {deficit:.0f} MW detectat. "
                    "Situație sub control. Monitorizez."
                ),
                action=None,
                action_label=None,
                confidence=0.80,
            )

        # ── Normal ──
        return AIDecision(
            status="normal",
            recommendation=(
                f"Rețea stabilă. Frecvență: {freq:.3f} Hz. "
                "Toți consumatorii critici conectați. Nicio acțiune necesară."
            ),
            action=None,
            action_label=None,
            confidence=0.99,
        )

    def _detect_oscillation(self) -> bool:
        """Detectează oscilații ritmice în istoricul frecvenței (semn FDIA)."""
        if len(self._freq_history) < 10:
            return False
        recent = self._freq_history[-10:]
        amplitude = max(recent) - min(recent)
        # Oscilație mare și ritmică = FDIA
        alternating = sum(
            1 for i in range(1, len(recent))
            if (recent[i] - recent[i-1]) * (recent[i-1] - recent[i-2] if i > 1 else -1) < 0
        )
        return amplitude > self.FREQ_OSCILLATION_THRESHOLD and alternating >= 6

    def _oscillation_confidence(self) -> float:
        if len(self._freq_history) < 2:
            return 0.5
        amplitude = max(self._freq_history[-10:]) - min(self._freq_history[-10:])
        return min(0.99, amplitude / 0.3)


# ─────────────────────────────────────────
# TEST
# ─────────────────────────────────────────
if __name__ == "__main__":
    from dataclasses import asdict
    ai = GridAI()

    print("=== NORMAL ===")
    d = ai.analyze({"frequency_hz": 50.01, "deficit_mw": 0, "anomaly_type": None, "nodes": []})
    print(f"Status: {d.status} | {d.recommendation}")

    print("\n=== CRIZĂ FIZICĂ ===")
    d = ai.analyze({"frequency_hz": 49.65, "deficit_mw": 1400, "anomaly_type": "physical", "nodes": [{"label": "CRN", "online": False}]})
    print(f"Status: {d.status} | Acțiune: {d.action}")
    print(f"Recomandare: {d.recommendation}")

    print("\n=== ATAC CYBER (simulez oscilații) ===")
    import math
    for i in range(15):
        freq = 50 + math.sin(i * 0.5) * 0.18
        d = ai.analyze({"frequency_hz": freq, "deficit_mw": 0, "anomaly_type": "fdia", "nodes": []})
    print(f"Status: {d.status} | Acțiune: {d.action}")
    print(f"Confidence: {d.confidence:.2f}")