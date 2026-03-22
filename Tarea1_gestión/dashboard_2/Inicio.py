import streamlit as st
import plotly.express as px
from utils_json import (
    load_all_data,
    style_fig,
    kpi_card,
    YEAR_COLORS,
    RATING_BAND_COLORS,
    make_binned_bar
)

st.set_page_config(
    page_title="Inicio",
    page_icon="🎬",
    layout="wide"
)

# =========================
# Carga de datos
# =========================
df, reviews_df = load_all_data()

# =========================
# KPIs globales
# =========================
total_movies = len(df)
total_reviews = len(reviews_df)
avg_rating = round(df["imdb_rating"].mean(), 2) if total_movies else 0
avg_duration = round(df["duration_minutes"].mean(), 1) if total_movies else 0

# =========================
# Encabezado visual
# =========================
st.markdown("""
<div style='padding: 1.25rem 1.4rem; border-radius: 18px;
background: linear-gradient(135deg, #EEF2FF 0%, #F8FAFC 100%);
border: 1px solid #E2E8F0; margin-bottom: 1rem;'>
    <div style='font-size: 2rem; font-weight: 800; color: #0F172A; margin-bottom: 0.3rem;'>
        Evaluación de películas candidatas a reestreno.
    </div>
    <div style='font-size: 1rem; color: #475569;'>
    Análisis general del conjunto de películas y reseñas.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# Tarjetas KPI
# =========================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        kpi_card("Películas", total_movies, "Muestra total analizada"),
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        kpi_card("Reseñas", total_reviews, "Opiniones procesadas"),
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        kpi_card("Rating promedio", avg_rating, "Calificación IMDb"),
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        kpi_card("Duración promedio", f"{avg_duration} min", "Tiempo medio de película"),
        unsafe_allow_html=True
    )

st.markdown("")

# =========================
# Primera fila de gráficos
# =========================
left, right = st.columns(2)

with left:
    # Distribución global de ratings en barras fijas
    fig = make_binned_bar(
        df=df,
        column="imdb_rating",
        bins=[5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0],
        labels=[
            "5.0-5.5", "5.5-6.0", "6.0-6.5", "6.5-7.0", "7.0-7.5",
            "7.5-8.0", "8.0-8.5", "8.5-9.0", "9.0-9.5", "9.5-10.0"
        ],
        title="Distribución global de ratings",
        x_label="Rango de rating IMDb",
        color_sequence=[
            "#60A5FA", "#3B82F6", "#2563EB", "#1D4ED8", "#6366F1",
            "#7C3AED", "#8B5CF6", "#14B8A6", "#0F766E", "#F59E0B"
        ]
    )
    fig = style_fig(fig, height=390, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    # Distribución global de duración en barras fijas
    fig = make_binned_bar(
        df=df,
        column="duration_minutes",
        bins=[0, 90, 110, 130, 150, 180, 1000],
        labels=["<=90", "91-110", "111-130", "131-150", "151-180", "180+"],
        title="Distribución global de duración",
        x_label="Rango de duración (min)",
        color_sequence=["#0EA5E9", "#06B6D4", "#14B8A6", "#10B981", "#22C55E", "#84CC16"]
    )
    fig = style_fig(fig, height=390, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)

# =========================
# Segunda fila de gráficos
# =========================
bottom_left, bottom_right = st.columns(2)

with bottom_left:
    # Composición por banda de rating
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
    # Películas por grupo de año
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
        labels={
            "year_group": "Grupo de año",
            "movie_count": "Número de películas"
        }
    )
    fig.update_traces(
        textposition="outside",
        textfont_size=16,
        cliponaxis=False
    )
    fig.update_layout(
        uniformtext_minsize=14,
        uniformtext_mode="hide",
        showlegend=False
    )
    fig = style_fig(fig, height=360, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)