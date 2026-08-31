import customtkinter as ctk
import asyncio
import threading
from typing import Dict, Any
from core.scraper import AdvancedScraper
from core.database import DatabaseManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ E-Commerce Intelligence Studio Pro")
        self.geometry("1000x700")

        self.db = DatabaseManager()
        self.scraped_count = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # En-tête
        self.header_frame = ctk.CTkFrame(self, corner_radius=10)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="⚡ E-Commerce Data Extractor & Scraper Engine", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=15)

        self.counter_label = ctk.CTkLabel(
            self.header_frame, 
            text="Extraits : 0", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3B82F6"
        )
        self.counter_label.pack(side="right", padx=20)

        # Formulaire
        self.config_frame = ctk.CTkFrame(self, corner_radius=10)
        self.config_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.url_text = ctk.CTkTextbox(self.config_frame, height=90, font=("Consolas", 12))
        self.url_text.pack(fill="x", padx=15, pady=10)
        self.url_text.insert("1.0", "https://httpbin.org/get\nhttps://example.com")

        self.controls = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.controls.pack(fill="x", padx=15, pady=(0, 10))

        self.conc_slider = ctk.CTkSlider(self.controls, from_=1, to=10, number_of_steps=9, width=150)
        self.conc_slider.set(3)
        self.conc_slider.pack(side="left", padx=5)

        self.slider_label = ctk.CTkLabel(self.controls, text="Vitesse (Threads: 3)")
        self.slider_label.pack(side="left", padx=5)
        self.conc_slider.configure(command=lambda v: self.slider_label.configure(text=f"Vitesse (Threads: {int(v)})"))

        self.btn_start = ctk.CTkButton(self.controls, text="🚀 Lancer l'extraction", fg_color="#2563EB", hover_color="#1D4ED8", command=self.start_scraping)
        self.btn_start.pack(side="right", padx=5)

        self.btn_export = ctk.CTkButton(self.controls, text="📊 Exporter Excel", fg_color="#10B981", hover_color="#059669", command=self.export_excel)
        self.btn_export.pack(side="right", padx=5)

        # Progression
        self.progress_bar = ctk.CTkProgressBar(self, height=8)
        self.progress_bar.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.progress_bar.set(0)

        # Live Feed
        self.feed_frame = ctk.CTkFrame(self, corner_radius=10)
        self.feed_frame.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="nsew")
        self.feed_frame.grid_columnconfigure(0, weight=1)
        self.feed_frame.grid_rowconfigure(1, weight=1)

        self.feed_title = ctk.CTkLabel(self.feed_frame, text="🟢 FLUX EN TEMPS RÉEL (LIVE DATA STREAM)", font=ctk.CTkFont(size=12, weight="bold"))
        self.feed_title.grid(row=0, column=0, padx=15, pady=5, sticky="w")

        self.textbox_live = ctk.CTkTextbox(self.feed_frame, font=("Consolas", 11), wrap="none")
        self.textbox_live.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        header = f"{'STATUT':<12} | {'PRIX':<18} | {'TITRE DU PRODUIT / URL':<60}\n"
        header += "-" * 95 + "\n"
        self.textbox_live.insert("end", header)

    def on_item_scraped(self, item: Dict[str, Any], progress: float):
        def _update_ui():
            self.scraped_count += 1
            self.counter_label.configure(text=f"Extraits : {self.scraped_count}")
            self.progress_bar.set(progress / 100.0)

            status_symbol = "🟢 [SUCCÈS]" if item["status"] == "SUCCÈS" else "🔴 [ÉCHEC]"
            line = f"{status_symbol:<12} | {item['price'][:16]:<18} | {item['title']:<60}\n"
            
            self.textbox_live.insert("end", line)
            self.textbox_live.see("end")

        self.after(0, _update_ui)

    def start_scraping(self):
        urls = [u.strip() for u in self.url_text.get("1.0", "end").strip().split("\n") if u.strip()]
        if not urls:
            return

        self.btn_start.configure(state="disabled")
        self.scraped_count = 0
        self.counter_label.configure(text="Extraits : 0")
        self.progress_bar.set(0)

        concurrency = int(self.conc_slider.get())
        threading.Thread(target=self._run_async, args=(urls, concurrency), daemon=True).start()

    def _run_async(self, urls, concurrency):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        scraper = AdvancedScraper(concurrency=concurrency)
        loop.run_until_complete(scraper.run(urls, real_time_callback=self.on_item_scraped))
        
        self.after(0, lambda: self.btn_start.configure(state="normal"))

    def export_excel(self):
        try:
            self.db.export_to_excel()
            self.textbox_live.insert("end", "\n📁 Exportation réussie vers export_produits.xlsx !\n")
            self.textbox_live.see("end")
        except Exception as e:
            self.textbox_live.insert("end", f"\n❌ Erreur export : {str(e)}\n")
