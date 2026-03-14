# 🛡️ GridSentinel: Scut Digital pentru Infrastructura Critică

**GridSentinel** este o soluție avansată de monitorizare și protecție a Rețelei Electrice de Transport (RET), concepută pentru a identifica și clasifica anomaliile de flux în timp real. Sistemul analizează parametrii electrici de la 31 de noduri strategice, oferind o barieră predictivă împotriva fluctuațiilor, erorilor tehnice și atacurilor cibernetice.

---

## ⚙️ Logica de Implementare Tehnică

Proiectul se bazează pe analiza fluxului de putere și a stabilității frecvenței, utilizând următoarele principii de procesare:

* **🔄 Evoluție Temporală și Persistență:** Sistemul nu analizează eșantioane izolate, ci fluxuri continue. Generatorul de date implementează o logică de „tranziție de stare”, ceea ce permite AI-ului să înțeleagă contextul temporal.
* **🔍 Identificarea Semnăturilor Digitale:** GridSentinel izolează tipul de anomalie prin analiza pattern-ului de date (ex: fluctuații fizice vs. atacuri cibernetice sinusoidale).
* **🌐 Arhitectură Station-Agnostic:** Algoritmul este antrenat pe legile fizice ale energiei (Hz, kV, MW), permițând scalarea pe orice nod nou fără reantrenare.

---

## 🚦 Matricea de Severitate

| Nivel | Tip Stare | Indicatori Tehnici | Impact Operațional |
| :--- | :--- | :--- | :--- |
| 🟢 **0** | **Nominal** | Frecvență stabilă (50Hz), tensiune nominală. | Operare optimă. |
| 🟡 **1** | **Atenție** | Deviații parametrice ușoare, zgomot de fond. | Monitorizare sporită. |
| 🟠 **2** | **Alertă** | Căderi de tensiune, eficiență scăzută a fluxului. | Intervenție tehnică. |
| 🔵 **3** | **Cyber** | Pattern-uri sinusoidale suspecte în frecvență. | Protocol securitate. |
| 🔴 **4** | **Critic** | Instabilitate severă, risc de colaps structural. | Redirecționare fluxuri. |
| ⚫ **5** | **Catastrofă** | Încetarea totală a fluxului (Blackout). | Restaurare sistem. |

---

## 🏗️ Arhitectura Proiectului

* **src/** – Nucleul logic: Generator de telemetrie evolutiv și motorul de decizie.
* **data/** – Depozit pentru setul de antrenament (100k rânduri) și stream-ul live.
* **models/** – Arhiva modelelor de Machine Learning antrenate pentru detecție.

---

## 👥 Echipa de Dezvoltare

* **Niki:** Project Manager & Data Architect
* **Tudor:** Machine Learning Engineer
* **Iustin:** Logic & Decision Engine
* **Alex:** UI/UX & Visualization Specialist
