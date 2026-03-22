import streamlit as st
import plotly.express as px
from utils_json  import (
    load_all_data, style_fig, kpi_card,
    GENRE_COLORS, YEAR_COLORS, RATING_BAND_COLORS
)

st.set_page_config(
    page_title="Inicio",
    page_icon="🎬",
    layout="wide"
)

df, reviews_df = load_all_data()

total_movies = len(df)
total_reviews = len(reviews_df)
avg_rating = round(df["imdb_rating"].mean(), 2) if total_movies else 0
avg_duration = round(df["duration_minutes"].mean(), 1) if total_movies else 0

st.markdown("""
<div style='padding: 1.25rem 1.4rem; border-radius: 18px;
background: linear-gradient(135deg, #EEF2FF 0%, #F8FAFC 100%);
border: 1px solid #E2E8F0; margin-bottom: 1rem;'>
    <div style='font-size: 2rem; font-weight: 800; color: #0F172A; margin-bottom: 0.3rem;'>
        IMDb Movie Dashboard
    </div>
    <div style='font-size: 1rem; color: #475569;'>
        Análisis general del conjunto de películas y reseñas.
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("Películas", total_movies, "Muestra total analizada"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Reseñas", total_reviews, "Opiniones procesadas"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("Rating promedio", avg_rating, "Calificación IMDb"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("Duración promedio", f"{avg_duration} min", "Tiempo medio de película"), unsafe_allow_html=True)

st.markdown("")

left, right = st.columns(2)

with left:
    fig = px.histogram(
        df,
        x="imdb_rating",
        nbins=12,
        color="genre",
        opacity=0.85,
        color_discrete_sequence=GENRE_COLORS,
        title="Distribución global de ratings",
        labels={"imdb_rating": "Rating IMDb", "count": "Frecuencia", "genre": "Género"}
    )
    fig = style_fig(fig, height=390, show_legend=True, legend_position="bottom")
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.histogram(
        df,
        x="duration_minutes",
        nbins=12,
        color="genre",
        opacity=0.85,
        color_discrete_sequence=GENRE_COLORS,
        title="Distribución global de duración",
        labels={"duration_minutes": "Duración (min)", "count": "Frecuencia", "genre": "Género"}
    )
    fig = style_fig(fig, height=390, show_legend=True, legend_position="bottom")
    st.plotly_chart(fig, use_container_width=True)

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    rating_band_df = (
        df.groupby("rating_band", as_index=False)
        .size()
        .rename(columns={"size": "movie_count"})
    )

    fig = px.pie(
        rating_band_df,
        names="rating_band",
        values="movie_count",
        hole=0.60,
        color_discrete_sequence=RATING_BAND_COLORS,
        title="Composición por banda de rating"
    )
    fig = style_fig(fig, height=360, show_legend=True, legend_position="bottom")
    st.plotly_chart(fig, use_container_width=True)

with bottom_right:
    year_count_df = (
        df.groupby("year_group", as_index=False)
        .size()
        .rename(columns={"size": "movie_count"})
    )

    fig = px.bar(
        year_count_df,
        x="year_group",
        y="movie_count",
        text="movie_count",
        color="year_group",
        color_discrete_sequence=YEAR_COLORS,
        title="Películas por grupo de año",
        labels={"year_group": "Grupo de año", "movie_count": "Número de películas"}
    )
    fig.update_traces(textposition="outside", textfont_size=16, cliponaxis=False)
    fig.update_layout(uniformtext_minsize=14, uniformtext_mode="hide")
    fig = style_fig(fig, height=360, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)