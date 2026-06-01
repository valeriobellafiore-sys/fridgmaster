import speech_recognition as sr
import json #

class InventoryManager:
    def __init__(self):
        self.ingredienti = []
        self.carica_dati() # Carica i dati salvati all'avvio

    # --- FUNZIONE SALVATAGGIO ---
    def salva_dati(self):
        with open("database.json", "w") as f:
            json.dump(self.ingredienti, f)

    def carica_dati(self):
        try:
            with open("database.json", "r") as f:
                self.ingredienti = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ingredienti = []

    # --- FUNZIONE STATISTICHE DIETA ---
    def analizza_dieta(self):
        # Definiamo i gruppi per la statistica
        gruppi = {
            "Carne": ["pollo", "manzo", "maiale", "carne", "tacchino"],
            "Pesce": ["tonno", "salmone", "merluzzo", "pesce"],
            "Pasta/Carb": ["pasta", "riso", "pane", "patate"],
            "Verdura": ["zucchine", "pomodori", "insalata", "carote"],
            "Legumi": ["fagioli", "lenticchie", "ceci", "piselli"]
        }
        
        conteggio = {"Carne": 0, "Pesce": 0, "Pasta/Carb": 0, "Verdura": 0, "Legumi": 0}
        
        # Analizziamo gli ingredienti nel frigo
        for ingrediente in self.ingredienti:
            ing_lower = ingrediente.lower()
            for categoria, parole_chiave in gruppi.items():
                if any(keyword in ing_lower for keyword in parole_chiave):
                    conteggio[categoria] += 1
        
        # Creiamo il report finale
        messaggio = "📊 STATISTICHE DIETA:\n"
        for cat, num in conteggio.items():
            messaggio += f"- {cat}: {num} prodotti\n"
        
        return messaggio
    def __init__(self):
        self.ingredienti = []

    def aggiungi_testo(self, testo):
        # Pulisce la stringa e divide gli ingredienti se separati da virgola
        nuovi = [i.strip().lower() for i in testo.split(",")]
        self.ingredienti.extend(nuovi)
        self.salva_dati() #
        return self.ingredienti

    def ascolta_voce(self):
        import speech_recognition as sr
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                print("In ascolto...") # Utile da vedere nel terminale
                audio = r.listen(source)
            testo_sentito = r.recognize_google(audio, language="it-IT").lower()
            print(f"Hai detto: {testo_sentito}")

            # 1. Comando per SVUOTARE TUTTO
            if "cancella tutto" in testo_sentito or "svuota" in testo_sentito:
                self.ingredienti = [] 
                self.salva_dati() # FONDAMENTALE: Salva il frigo vuoto nel file
                return "Inventario svuotato completamente"

            # 2. Comando per RIMUOVERE UN SINGOLO INGREDIENTE
            comandi_rimozione = ["cancella", "rimuovi", "togli", "elimina"]
            for comando in comandi_rimozione:
                if comando in testo_sentito:
                    # Togliamo il comando dal testo (es: "cancella latte" diventa "latte")
                    ingrediente_da_togliere = testo_sentito.replace(comando, "").strip()
                    
                    if ingrediente_da_togliere in self.ingredienti:
                        self.ingredienti.remove(ingrediente_da_togliere)
                        self.salva_dati()
                        return f"Ho rimosso {ingrediente_da_togliere}"
                    else:
                        # Se dici "cancella latte" ma il latte non c'è, fermiamo tutto qui
                        # per evitare che passi alla fase 3 e aggiunga "cancella"
                        return f"Non trovato: {ingrediente_da_togliere}"

            # 3. Logica standard per AGGIUNGERE UN INGREDIENTE
            parole_da_eliminare = ["aggiungi ", "metti ", "nel frigo", "inserisci "]
            per_lista = testo_sentito
            for parola in parole_da_eliminare:
                per_lista = per_lista.replace(parola, "")
            ingrediente_pulito = per_lista.strip()

            if ingrediente_pulito:
                self.ingredienti.append(ingrediente_pulito)
                self.salva_dati() # FONDAMENTALE: Salva il nuovo ingrediente nel file
                return f"Aggiunto {ingrediente_pulito}"

        except sr.UnknownValueError:
            print("Non ho capito l'audio")
        except Exception as e:
            print(f"Errore vocale: {e}")
            
        return None

    def svuota_inventario(self):
        self.ingredienti = []
        return "Inventario svuotato."