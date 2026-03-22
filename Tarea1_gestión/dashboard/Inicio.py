import streamlit as st

st.set_page_config(
    page_title="IMDb Dashboard",
    page_icon="🎬",
    layout="wide"
)

st.title("IMDb Análisis de películas")
st.markdown("""
Este cuadro de mando analiza películas y reseñas obtenidas mediante web scraping desde IMDb de 5 géneros: "Comedia, Acción, Drama, Horror, Animación".

### Flujo del proyecto
1. Extracción de películas y reseñas con Selenium.
2. Almacenamiento en JSON y posteriormente en MySQL.
3. Transformación y limpieza con pandas.
4. Visualización interactiva.
5. Análisis de sentimiento de reseñas.

Usa el menú lateral para navegar entre las páginas.
""")
