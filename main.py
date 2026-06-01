import webbrowser # Aggiunto per aprire i tutorial nel browser
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.audio import SoundLoader
from kivy.uix.image import AsyncImage
from kivy.clock import Clock

# Import dei componenti KivyMD necessari
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton, MDIconButton

# Importiamo i blocchi logici esterni
from fridge_logic import InventoryManager
from api_manager import APIManager
from preferiti_manager import PreferitiManager

# Inizializziamo i gestori
inventory = InventoryManager()
recipes = APIManager()


class RecipeScreen(Screen):
    def mostra_paywall(self):
        # Questo richiama la funzione definita nell'App principale
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        # Se la funzione mostra_paywall è in MainScreen, la richiamiamo da lì
        main_screen = app.root.get_screen('main')
        main_screen.mostra_paywall()

class FavoritesScreen(Screen):
    def svuota_tutto(self):
        from preferiti_manager import PreferitiManager
        import json
        manager = PreferitiManager()
        # Svuotiamo il file JSON
        with open("preferiti.json", 'w') as f:
            json.dump([], f)
        # Puliamo la grafica
        if hasattr(self.ids, 'contenitore_preferiti'):
            self.ids.contenitore_preferiti.clear_widgets()

    def on_enter(self):
        # 1. Puliamo la lista prima di ricaricare (per evitare duplicati)
        self.ids.contenitore_preferiti.clear_widgets()
        
        # 2. Carichiamo i dati
        from preferiti_manager import PreferitiManager
        manager = PreferitiManager()
        preferiti = manager.carica_tutti()

        # 3. Cicliamo sui preferiti e creiamo le card grafiche
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        
        for ricetta in preferiti:
            # Qui creiamo una card per ogni ricetta (puoi personalizzare questo layout)
            card = MDCard(size_hint_y=None, height="100dp", padding="10dp")
            lbl = MDLabel(text=ricetta.get('nome', 'Senza nome'))
            card.add_widget(lbl)
            
            # Aggiungiamo la card al contenitore
            self.ids.contenitore_preferiti.add_widget(card)


class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        # Stato iniziale dell'utente (Free di base)
        self.premium = False

    # FUNZIONE PER IL CUORICINO (RISOLVE IL CRASH)
    def toggle_preferito(self, button, ricetta):
        from preferiti_manager import PreferitiManager
        manager = PreferitiManager()
        
        # Il manager fa il lavoro sporco (aggiunge o toglie)
        is_pieno = manager.toggle(ricetta)
        
        # Cambiamo l'icona del bottone graficamente
        button.icon = "heart" if is_pieno else "heart-outline"

    # FUNZIONE PER IL TUTORIAL (RISOLVE PAGINA SCADUTA)
    def apri_tutorial(self, url):
        import webbrowser
        print(f"Apertura del tutorial: {url}")
        webbrowser.open(url)

    def aggiungi_ingrediente(self):
        from kivy.core.audio import SoundLoader
        testo = self.ids.input_testo.text.strip()
        if testo:
            inventory.aggiungi_testo(testo)
            inventory.salva_dati()
            
            # RIPRODUCI SUONO AGGIUNTA
            suono = SoundLoader.load('suoni/aggiunta.mp3')
            if suono:
                suono.play()
                
            self.ids.input_testo.text = ""  # Pulisce la barra di scrittura
            self.aggiorna_lista_visiva()

    def aggiorna_lista_visiva(self):
        from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget
        # AGGIORNA IL CONTATORE NUMERICO NELL'INTERFACCIA
        quanti = len(inventory.ingredienti)
        self.ids.contatore_ingredienti.text = f"Cibi: {quanti}"
        
        # 1. Trova la lista nell'interfaccia e svuotala
        lista_kivy = self.ids.lista_ingredienti
        lista_kivy.clear_widgets()

        # 2. Se non ci sono ingredienti, aggiungi un messaggio semplice
        if not inventory.ingredienti:
            lista_kivy.add_widget(OneLineAvatarIconListItem(text="Il frigo è vuoto..."))
            return

        # 3. Per ogni ingrediente, crea una riga con il cestino
        for ing in inventory.ingredienti:
            item = OneLineAvatarIconListItem(text=ing)
            
            # Crea l'icona del cestino a destra
            cestino = IconRightWidget(icon="delete")
            # Diciamo al cestino cosa fare quando viene cliccato
            cestino.bind(on_release=lambda x, i=ing: self.rimuovi_da_tasto(i))
            
            item.add_widget(cestino)
            lista_kivy.add_widget(item)

    def rimuovi_da_tasto(self, ingrediente):
        # Rimuove l'ingrediente dalla logica e salva
        if ingrediente in inventory.ingredienti:
            inventory.ingredienti.remove(ingrediente)
            inventory.salva_dati()
            
            # RIPRODUCI SUONO RIMOZIONE
            suono = SoundLoader.load('suoni/rimuovi.mp3') 
            if suono:
                suono.play()
                
            # Rinfresca la lista a video
            self.aggiorna_lista_visiva()

    def avvia_voce(self): 
        # 1. Chiama la logica e salva la risposta
        risultato = inventory.ascolta_voce()
        
        # 2. Scegliamo il suono in base a cosa è successo
        if risultato == "Inventario svuotato completamente":
            suono = SoundLoader.load('suoni/rimuovi.mp3') 
        else:
            suono = SoundLoader.load('suoni/aggiunta.mp3')
            
        # 3. Riproduci il suono scelto
        if suono:
            suono.play()
            
        # 4. Aggiorna la lista visiva
        self.aggiorna_lista_visiva()

    def cerca_ricette(self, premium_mode=False, *args):
        from preferiti_manager import PreferitiManager
        manager = PreferitiManager()
        lista_preferiti = manager.carica_tutti()

        if not isinstance(premium_mode, bool):
            premium_mode = self.premium
        
        print(f"DEBUG: Ricerca avviata. Modalità Premium: {premium_mode}")

        try:
            ingrediente_cercato = self.ids.input_ingrediente.text.strip()
        except AttributeError:
            ingrediente_cercato = "riso"

        if not ingrediente_cercato:
            return

        print(f"Sto cercando le ricette migliori online per: {ingrediente_cercato}...")
        risultato = recipes.ottieni_ricette_online(inventory.ingredienti, premium_mode)

        try:
            schermata_ricette = self.manager.get_screen('recipes')
        except Exception:
            schermata_ricette = self.parent.get_screen('recipes')

        self.manager.current = 'recipes'

        # Logica per trovare dove aggiungere i widget
        contenitore_lista = None
        if hasattr(schermata_ricette, 'ids') and 'contenitore_risultati' in schermata_ricette.ids:
            contenitore_lista = schermata_ricette.ids.contenitore_risultati
        elif hasattr(schermata_ricette, 'ids') and 'lista_ricette' in schermata_ricette.ids:
            contenitore_lista = schermata_ricette.ids.lista_ricette
        else:
            for widget in schermata_ricette.walk():
                if widget.__class__.__name__ in ['MDBoxLayout', 'BoxLayout'] and widget.id != 'top_bar':
                    contenitore_lista = widget
                    break

        if contenitore_lista is None:
            contenitore_lista = schermata_ricette

        contenitore_lista.clear_widgets()

        if not risultato:
            lbl_vuoto = MDLabel(
                text="Nessuna ricetta trovata.\nProva con un altro ingrediente!",
                halign="center", font_style="H6", size_hint_y=None, height="100dp"
            )
            contenitore_lista.add_widget(lbl_vuoto)
            return

        box_impilatore = MDBoxLayout(orientation='vertical', spacing="14dp", padding="12dp", size_hint_y=None)
        box_impilatore.bind(minimum_height=box_impilatore.setter('height'))

        for r in risultato:
            # Controllo se la ricetta è già nei preferiti
            is_fav = any(p.get('nome') == r.get('nome') for p in lista_preferiti)
            icona_cuore = "heart" if is_fav else "heart-outline"
            
            card = MDCard(orientation='vertical', padding="10dp", spacing="5dp", size_hint_x=1, size_hint_y=None, height="220dp", radius=[15], md_bg_color=(1, 1, 1, 1))
            
            box_sup = MDBoxLayout(orientation='horizontal', size_hint_y=0.7, spacing="10dp")
            foto_ricetta = AsyncImage(source=r.get("immagine", "assets/cucina.jpg"), size_hint_x=None, width="100dp")
            box_sup.add_widget(foto_ricetta)
            
            info_box = MDBoxLayout(orientation='vertical', size_hint_x=1, spacing="2dp")
            riga_titolo = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="35dp")
            riga_titolo.add_widget(MDLabel(text=r.get("nome", "Ricetta").upper(), bold=True, font_style="Subtitle1"))
            
            # Bottone cuore (Questo era già corretto)
            riga_titolo.add_widget(MDIconButton(
                icon=icona_cuore, 
                size_hint=(None, None), 
                size=("40dp", "40dp"), 
                on_release=lambda x, data=r: self.toggle_preferito(x, data)
            ))
            
            info_box.add_widget(riga_titolo)
            info_box.add_widget(MDLabel(text=f"⏱️ {r.get('tempo', 'N/D')} | 📊 {r.get('difficolta', 'N/D')}", font_style="Caption"))
            box_sup.add_widget(info_box)
            card.add_widget(box_sup)
            
            riga_pulsanti = MDBoxLayout(orientation='horizontal', size_hint_y=0.3, spacing="10dp", padding=["5dp", "0dp", "5dp", "5dp"])
            chiave_amazon = "+".join(r.get("ingredienti_mancanti", ["riso", "zafferano"]))
            
            # MODIFICATO: aggiunto ric=r per bloccare la ricetta giusta nel bottone
            btn_amazon = MDFillRoundFlatButton(
                text="Compra ingredienti", 
                size_hint_x=0.45, 
                font_size="11sp", 
                md_bg_color=(1, 0.55, 0, 1), 
                on_release=lambda x, ric=r: self.apri_link_esterno(f"https://www.amazon.it/s?k={'+'.join(ric.get('ingredienti_mancanti', ['riso', 'zafferano']))}&tag=gnamstyle-21")
            )
            
            # MODIFICATO: aggiunto ric=r per bloccare la ricetta giusta nel bottone
            btn_web = MDFillRoundFlatButton(
                text="Vedi tutorial GialloZafferano", 
                size_hint_x=0.55, 
                font_size="11sp", 
                md_bg_color=(0.1, 0.6, 0.2, 1), 
                on_release=lambda x, ric=r: self.apri_link_esterno(ric.get('url_esterno', ''))
            )
            
            riga_pulsanti.add_widget(btn_amazon)
            riga_pulsanti.add_widget(btn_web)
            card.add_widget(riga_pulsanti)
            box_impilatore.add_widget(card)
        
        contenitore_lista.add_widget(box_impilatore)

    def mostra_paywall(self, *args):
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDRaisedButton, MDFlatButton

        # Contenitore principale
        contenuto = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding="20dp",
            size_hint_y=None,
            height="340dp",
            md_bg_color=(0.12, 0.12, 0.12, 1),
            radius=[20, 20, 20, 20]
        )

        contenuto.add_widget(MDLabel(
            text="PASSA A GNAM STYLE PREMIUM 👑",
            bold=True,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H6",
            halign="center",
            size_hint_y=None,
            height="40dp"
        ))

        testo_caratteristiche = (
            "👑 Accesso illimitato a +10.000 ricette\n"
            "🚫 Zero banner pubblicitari\n"
            "📊 Statistiche avanzate e piani per la dieta"
        )
        contenuto.add_widget(MDLabel(
            text=testo_caratteristiche,
            theme_text_color="Custom",
            text_color=(0.8, 0.8, 0.8, 1),
            font_style="Body1",
            halign="left",
            size_hint_y=None,
            height="70dp"
        ))

        testo_prezzi = (
            "Scegli il tuo piano ideale:\n\n"
            "▶ MENSILE: 1,99€ / mese (Annulli quando vuoi)\n"
            "🌟 ANNUALE: 19,99€ / anno (Risparmi il 16%! — 2 Mesi Gratis)"
        )
        contenuto.add_widget(MDLabel(
            text=testo_prezzi,
            bold=True,
            theme_text_color="Custom",
            text_color=(1, 0.4, 0, 1),
            font_style="Subtitle1",
            halign="left",
            size_hint_y=None,
            height="90dp"
        ))

        box_pulsanti = MDBoxLayout(
            orientation="horizontal",
            spacing="15dp",
            size_hint_y=None,
            height="45dp"
        )

        btn_chiudi = MDFlatButton(
            text="MAGARI DOPO",
            text_color=(1, 1, 1, 0.6),
            theme_text_color="Custom",
            on_release=lambda x: self.dialogo_paywall.dismiss()
        )

        btn_attiva = MDRaisedButton(
            text="ATTIVA ABBONAMENTO",
            md_bg_color=(1, 0.4, 0, 1),
            text_color=(1, 1, 1, 1),
            on_release=self.attiva_abbonamento_finto
        )

        box_pulsanti.add_widget(btn_chiudi)
        box_pulsanti.add_widget(btn_attiva)
        contenuto.add_widget(box_pulsanti)

        self.dialogo_paywall = MDDialog(
            type="custom",
            content_cls=contenuto,
            auto_dismiss=False,
        )
        self.dialogo_paywall.open()

    def mostra_dialogo_ingredienti(self, nome_piatto, lista_ing):
        """Mostra una finestra pop-up con la lista degli ingredienti necessari."""
        from kivymd.uix.dialog import MDDialog
        
        testo_ingredienti = "\n".join([f"• {i.capitalize()}" for i in lista_ing]) if lista_ing else "Nessun ingrediente specificato."
        
        dialogo = MDDialog(
            title=f"Ingredienti per {nome_piatto}:",
            text=testo_ingredienti,
            buttons=[MDFlatButton(text="OK", text_color=(1, 0.4, 0, 1), on_release=lambda x: dialogo.dismiss())]
        )
        dialogo.open()

    def apri_link_esterno(self, url):
        """Apre il link web (GialloZafferano) nel browser per mostrare i banner."""
        import webbrowser
        if url:
            print(f"Apertura del sito esterno con pubblicità: {url}")
            webbrowser.open(url)

    def attiva_abbonamento_finto(self, instance):
        if hasattr(self, 'dialogo_paywall') and self.dialogo_paywall:
            self.dialogo_paywall.dismiss()
            self.dialogo_paywall = None 
        
        self.premium = True
        
        from kivymd.uix.snackbar import MDSnackbar

        snackbar = MDSnackbar(
            md_bg_color=(1, 0.4, 0, 1),
            duration=3,
        )
        snackbar.add_widget(MDLabel(
            text="👑 Abbonamento Attivato! Benvenuto in Gnam Style Premium!",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            halign="center",
        ))
        snackbar.open()
        
        self.cerca_ricette(True)


class FridgeMasterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        
        # Carica il file KV
        Builder.load_file('interfaccia.kv')
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(RecipeScreen(name='recipes'))
        sm.add_widget(FavoritesScreen(name='favorites')) # <--- AGGIUNGI QUESTA
        
        return sm

    def on_start(self):
        try:
            inventory.carica_dati()
            print(f"Dati caricati dall'archivio: {inventory.ingredienti}")
            
            # Usiamo un piccolo ritardo (Clock) per dare il tempo a Kivy di 
            # agganciare lo schermo prima di riempire la lista visiva
            Clock.schedule_once(self.inizializza_interfaccia, 0.2)
        except Exception as e:
            print(f"Errore durante l'avvio: {e}")

    def inizializza_interfaccia(self, dt):
        if self.root and self.root.has_screen('main'):
            schermo_principale = self.root.get_screen('main')
            schermo_principale.aggiorna_lista_visiva()


if __name__ == "__main__":
    FridgeMasterApp().run()