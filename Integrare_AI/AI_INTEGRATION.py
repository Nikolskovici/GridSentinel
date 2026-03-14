import numpy as np
from sklearn.ensemble import IsolationForest

class CyberDefenseAI:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        # Antrenăm cu date normale (50Hz)
        date_training = np.random.normal(50.0, 0.01, (1000, 1))
        self.model.fit(date_training)

    def analizeaza_flux_date(self, date_noi):
        pred = self.model.predict(date_noi)
        if -1 in pred:
            return "🚨 ALERTĂ: Anomalie detectată (Posibil atac de injectare date)!"
        return None

class GridOptimizer:
    def calculeaza_prioritate_reala(self, n):
        importanta = {'spital': 100, 'militar': 90, 'transport': 70, 'rezidential': 50, 'industrial': 30, 'comercial': 10}
        scor = importanta.get(n.get('tip', 'rezidential'), 40)
        if n.get('smart'): scor += 10
        if n.get('mw', 0) > 80: scor -= 5
        return scor

    def genereaza_plan_dinamic(self, lista_noduri, deficit):
        if deficit <= 0: return None
        for n in lista_noduri:
            n['prio'] = self.calculeaza_prioritate_reala(n)
        
        sortati = sorted(lista_noduri, key=lambda x: x['prio'])
        plan = []
        economisit = 0
        
        for n in sortati:
            if economisit >= deficit: break
            smart = n.get('smart', False)
            metoda = "LIMITARE (THROTTLE)" if smart else "DECONECTARE (SHUTDOWN)"
            reducere = n['mw'] * 0.5 if smart else n['mw']
            
            plan.append({
                "locatie": n['nume'],
                "tip": n['tip'].upper(),
                "actiune": metoda,
                "detalii": f"Actionare releu {n['nume']} pentru {metoda}",
                "mw_salvati": reducere,
                "motivatie": f"Prioritate {n['prio']} (Triaj automat pe importanta {n['tip']})"
            })
            economisit += reducere
        return plan