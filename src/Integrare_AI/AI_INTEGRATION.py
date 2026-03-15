class CyberGridOptimizer:
    def __init__(self):
        # Topologia rețelei pentru izolare (Grafuri)
        self.topologie_retea = {
            "CLJ": ["ORD", "BIS", "TGM", "PFR"],
            "BRZ": ["BUC", "VID", "BCU", "PIT"],
            "BUC": ["BRZ", "CAL", "SLT", "CST"],
            "PFR": ["TMS", "CLJ", "ISN", "TRC"],
            "VID": ["BRZ", "SBU", "PIT"],
            "BCN": ["SUC", "BCU", "TGM"]
        }
        
        # Tipuri de anomalii cibernetice detectate de modelul ML
        self.tipuri_atac = {
            "DOS": "Denial of Service (Saturație trafic SCADA)",
            "MITM": "Man-in-the-Middle (Interceptare date senzori)",
            "INJ": "Injection Attack (Comenzi false în sistem)",
            "MAL": "Malware (Compromitere nod control)"
        }

    def analizeaza_anomalie_cyber(self, probabilitate):
        """Determină tipul de atac în funcție de amprenta probabilității."""
        if probabilitate > 0.90: return self.tipuri_atac["DOS"]
        if probabilitate > 0.75: return self.tipuri_atac["INJ"]
        if probabilitate > 0.50: return self.tipuri_atac["MITM"]
        if probabilitate > 0.30: return self.tipuri_atac["MAL"]
        return "Activitate suspectă nespecificată"

    def evalueaza_stare_retea(self, deficit_mw, probabilitate_cyber, nod_suspect=None):
        nivel = 0
        status = "Parametri Nominali"
        solutie = "Monitorizare continuă."
        muchii_de_taiat = []
        detalii_cyber = ""

        # Dacă există risc cyber, identificăm tipul de anomalie
        if probabilitate_cyber > 0.30:
            detalii_cyber = self.analizeaza_anomalie_cyber(probabilitate_cyber)

        # Logica de decizie combinată (Energie + Securitate)
        if deficit_mw > 400 or (probabilitate_cyber > 0.85 and deficit_mw > 250):
            nivel = 5
            status = f"COLAPS IMINENT / {detalii_cyber.upper()}"
            solutie = "CRITIC: Izolare fizică totală. Treceți nodul în regim de insulă."
            if nod_suspect: muchii_de_taiat = self._calculeaza_izolare(nod_suspect)

        elif deficit_mw > 250 or probabilitate_cyber > 0.70:
            nivel = 4
            status = f"ATAC DETECTAT: {detalii_cyber}"
            solutie = "URGENȚĂ: Izolare logică. Redirecționare trafic prin noduri sigure."
            if nod_suspect: muchii_de_taiat = self._calculeaza_izolare(nod_suspect)

        elif deficit_mw > 150 or probabilitate_cyber > 0.50:
            nivel = 3
            status = "INSTABILITATE / RISC CYBER MODERAT"
            solutie = "AVERTIZARE: Monitorizare intensivă SCADA. Resetare chei criptografice."
        
        elif probabilitate_cyber > 0.30:
            nivel = 2
            status = f"ANOMALIE: {detalii_cyber}"
            solutie = "ALERTĂ: Analiză forensic pe pachetele suspecte. Activare Firewall Layer 7."

        elif deficit_mw > 50:
            nivel = 1
            status = "DEFICIT ENERGETIC MINOR"
            solutie = "ROUTINĂ: Pornire rezervă terțiară."

        return {
            "nivel_severitate": nivel,
            "status_general": status,
            "nod_afectat": nod_suspect if nivel >= 2 else None,
            "recomandare_ai": solutie,
            "muchii_de_taiat": muchii_de_taiat,
            "deficit_curent": deficit_mw,
            "tip_atac": detalii_cyber
        }
        
    def _calculeaza_izolare(self, nod):
        vecini = self.topologie_retea.get(nod, [])
        return [f"{nod}-{vecin}" for vecin in vecini]