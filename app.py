import streamlit as st
import pandas as pd
import asyncio
from scraper import AdvancedScraper
from database import DatabaseManager

st.set_page_config(page_title="E-Commerce Scraper Pro", page_icon="⚡", layout="wide")

st.title("⚡ E-Commerce Intelligence Studio Pro")
st.subheader("Scraper & Analyse de prix en temps réel")

# Initialisation de la BD
db = DatabaseManager()

# Sidebar pour la configuration
st.sidebar.header("⚙️ Configuration")
max_threads = st.sidebar.slider("Vitesse (Nombre de threads concurrents)", 1, 10, 3)

# Zone de saisie d'URL
urls_input = st.text_area("Entrez les URLs des produits à analyser (une par ligne) :", height=150, 
                          placeholder="https://example.com/produit1\nhttps://example.com/produit2")

if st.button("🚀 Lancer l'extraction", type="primary"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    if not urls:
        st.warning("Veuillez saisir au moins une URL valide.")
    else:
        st.info(f"Traitement de {len(urls)} URLs en cours...")
        scraper = AdvancedScraper(db_manager=db, max_concurrency=max_threads)
        
        # Exécution du scraping
        results = asyncio.run(scraper.scrape_batch(urls))
        st.success("Extraction terminée avec succès !")

# Section d'affichage des résultats
st.markdown("---")
st.header("📊 Données extraites")

data = db.fetch_all_products() if hasattr(db, 'fetch_all_products') else []

if data:
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Export Excel
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les résultats (CSV/Excel)",
        data=csv,
        file_name="produits_extraits.csv",
        mime="text/csv",
    )
else:
    st.write("Aucune donnée disponible pour le moment.")
