# 🛡️ GridSentinel - Smart Grid Defense System

Sistem avansat de monitorizare și detecție a anomaliilor pentru rețelele electrice (Transelectrica).

## 🚀 Funcționalități
- **Digital Twin Telemetry:** Generare de date sintetice (frecvență, tensiune, fluxuri MW).
- **AI Anomaly Detection:** Identificarea automată a atacurilor cibernetice (FDIA) și a defectelor tehnice.
- **Triage System:** Clasificarea incidentelor pe 6 nivele de severitate.
        -Nivel 0: Cazul default in care toate sistemele si senzorii functioneaza in parametrii normali.
        -Nivel 1: Mici deviatii de la normalitate detectate, notificare echipei de ingineri.
        -Nivel 2: Anomalie descoperita, inginerul principal este notificat si trebuie sa ia o decizie.
        -Nivel 3: Multiple anomalii detectate, pericol grav de de avarie a retelei. Echipa de ingineri
                trebuie sa ia o decizie.
        -Nivel 4: Pericol iminent de avarie si intrerupere a serviciilor de curent electric. Alarma activata
                si fiecare inginer in functie anuntat.
        -Nivel 5: Catastrofa. Fiecare inginer este anuntat indiferent daca este in tura si este rugat sa
                raporteze la centrul sau regional.
- **Action Plans:** Protocoale automate de intervenție pentru dispeceri.

## 🛠️ Tehnologii
- Python (Pandas, NumPy, Scikit-Learn, tensorflow)
- Streamlit (Dashboard interactiv)

## 👤 Echipa
- **Niki** (Data Architect & Project Lead)
- **Tudor** (AI Specialist)
- **Iustin** (Logic & Integration)
- **Alex** (UI/UX Developer)
