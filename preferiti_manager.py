import json
import os

class PreferitiManager:
    def __init__(self, filename="preferiti.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)

    def carica_tutti(self):
        with open(self.filename, 'r') as f:
            return json.load(f)
    
    def rimuovi_per_id(self, ricetta_id):
        data = self.carica_tutti()
        # Filtra la lista tenendo solo le ricette che NON hanno quell'ID
        nuova_lista = [r for r in data if r.get('id') != ricetta_id]
        with open(self.filename, 'w') as f:
            json.dump(nuova_lista, f, indent=4)

    def toggle(self, ricetta):
        data = self.carica_tutti()
        
        # Usiamo l'ID invece del nome per essere più sicuri (è più preciso)
        id_ricetta = ricetta.get('id')
        esistente = next((r for r in data if r.get('id') == id_ricetta), None)

        if esistente:
            data.remove(esistente)
            stato = False
        else:
            data.append(ricetta)
            stato = True
        
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)
        
        return stato