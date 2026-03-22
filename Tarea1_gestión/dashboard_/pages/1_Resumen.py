import streamlit as st
import plotly.express as px
from utils_json import (
    load_all_data,
    render_filters,
    style_fig,
    style_bar_text,
    kpi_card,
    GENRE_COLORS,
    make_binned_bar_by_group
)

st.set_page_config(
    page_title="Resumen",
    page_icon="🎬",
    layout="wide"
)

st.title("Resumen")

df, reviews_df = load_all_data()
filtered = render_filters(df)

if filtered.empty:
    st.warning("No hay datos con los filtros actuales.")
    st.stop()

# =========================
# KPIs de resumen
# =========================
avg_rating = round(filtered["imdb_rating"].mean(), 2)
avg_duration = round(filtered["duration_minutes"].mean(), 1)
avg_sentiment = round(filtered["avg_sentiment_score"].mean(), 3)
avg_review_length = round(filtered["avg_review_length"].mean(), 1)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("Rating promedio", avg_rating, "Promedio IMDb"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Duración promedio", f"{avg_duration} min", "Tiempo medio"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("Sentimiento promedio", avg_sentiment, "Tono medio de reseñas"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("Longitud media", f"{avg_review_length} palabras", "Reseñas"), unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    # Gráfico 1:
    # Compara el rating promedio IMDb entre los distintos géneros.
    avg_rating_genre = (
        filtered.groupby("genre", as_index=False)["imdb_rating"]
        .mean()
        .sort_values("imdb_rating", ascending=True)
    )

    fig = px.bar(
        avg_rating_genre,
        x="imdb_rating",
        y="genre",
        orientation="h",
        text="imdb_rating",
        color="genre",
        color_discrete_sequence=GENRE_COLORS,
        title="Rating promedio por género",
        labels={
            "imdb_rating": "Rating promedio",
            "genre": "Género"
        }
    )
    fig = style_bar_text(fig, axis="x", size=16)
    fig = style_fig(fig, height=390, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    # Gráfico 2:
    # Muestra cómo se distribuye la duración de las películas dentro de cada género.
    fig = px.box(
        filtered,
        x="genre",
        y="duration_minutes",
        color="genre",
        color_discrete_sequence=GENRE_COLORS,
        title="Distribución de duración por género",
        labels={
            "genre": "Género",
            "duration_minutes": "Duración (min)"
        }
    )
    fig = style_fig(fig, height=390, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    # Gráfico 3:
    # Reemplaza el histograma por barras agrupadas para que no cambie al subirlo.
    # Muestra la distribución del rating según el grupo de año.
    fig = make_binned_bar_by_group(
        df=filtered,
        column="imdb_rating",
        group_col="year_group",
        bins=[5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0],
        labels=[
            "5.0-5.5", "5.5-6.0", "6.0-6.5", "6.5-7.0", "7.0-7.5",
            "7.5-8.0", "8.0-8.5", "8.5-9.0", "9.0-9.5", "9.5-10.0"
        ],
        title="Distribución del rating por grupo de año",
        x_label="Rango de rating IMDb",
        group_label="Grupo de año",
        color_sequence=["#3B82F6", "#6366F1", "#8B5CF6", "#14B8A6", "#F59E0B"],
        barmode="group"
    )
    fig = style_fig(fig, height=360, show_legend=True, legend_position="bottom")
    st.plotly_chart(fig, use_container_width=True)

with bottom_right:
    # Gráfico 4:
    # Heatmap que cruza grupo de año con banda de rating para ver patrones de concentración.
    heat_df = (
        filtered.groupby(["year_group", "rating_band"], as_index=False)
        .size()
        .rename(columns={"size": "movie_count"})
    )
    heatmap = heat_df.pivot(index="year_group", columns="rating_band", values="movie_count").fillna(0)

    fig = px.imshow(
        heatmap,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Heatmap: grupo de año vs banda de rating"
    )
    fig = style_fig(fig, height=360, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)