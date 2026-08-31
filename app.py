import asyncio
import pandas as pd
import streamlit as st
from scraper import AdvancedScraper

st.set_page_config(
    page_title="E-Commerce Intelligence Studio Pro",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ E-Commerce Intelligence Studio Pro")
st.markdown("Extraisez les données produits en temps réel depuis n'importe quelle URL.")

# Saisie des URLs
urls_input = st.text_area(
    "Entrez les URLs des produits à analyser (une par ligne) :",
    height=150,
    placeholder="https://exemple.com/produit1\nhttps://exemple.com/produit2"
)

# Paramètres
col1, col2 = st.columns(2)
with col1:
    max_threads = st.slider("Vitesse / Concurrence (requêtes simultanées)", 1, 10, 3)

if st.button("🚀 Lancer l'extraction", type="primary"):
    urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
    
    if not urls:
        st.warning("Veuillez saisir au moins une URL valide.")
    else:
        st.info(f"Traitement de {len(urls)} URL(s) en cours...")
        
        # Initialisation sécurisée
        try:
            scraper = AdvancedScraper(max_concurrency=max_threads)
        except TypeError:
            scraper = AdvancedScraper()

        # Exécution asynchrone sécurisée
        async def run_scraper():
            if hasattr(scraper, 'scrape_urls'):
                return await scraper.scrape_urls(urls)
            elif hasattr(scraper, 'scrape_batch'):
                return await scraper.scrape_batch(urls)
            elif hasattr(scraper, 'run'):
                return await scraper.run(urls)
            elif hasattr(scraper, 'scrape'):
                return await scraper.scrape(urls)
            else:
                raise AttributeError("Aucune méthode d'extraction trouvée.")

        with st.spinner("Extraction des données en arrière-plan via Playwright..."):
            try:
                results = asyncio.run(run_scraper())
                
                if results:
                    st.success("Extraction terminée avec succès !")
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    
                    # Bouton d'export CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Télécharger les données (CSV)",
                        data=csv,
                        file_name="resultats_extraction.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Aucune donnée n'a pu être extraite des URLs fournies.")
            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'exécution : {e}")
