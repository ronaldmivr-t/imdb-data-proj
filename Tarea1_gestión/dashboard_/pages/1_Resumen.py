import streamlit as st
import plotly.express as px
from utils_json  import (
    load_all_data, render_filters, style_fig, style_bar_text, kpi_card,
    GENRE_COLORS
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
        labels={"imdb_rating": "Rating promedio", "genre": "Género"}
    )
    fig = style_bar_text(fig, axis="x", size=16)
    fig = style_fig(fig, height=390, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.box(
        filtered,
        x="genre",
        y="duration_minutes",
        color="genre",
        color_discrete_sequence=GENRE_COLORS,
        title="Distribución de duración por género",
        labels={"genre": "Género", "duration_minutes": "Duración (min)"}
    )
    fig = style_fig(fig, height=390, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    fig = px.histogram(
        filtered,
        x="imdb_rating",
        nbins=12,
        color="year_group",
        title="Distribución del rating por grupo de año",
        labels={"imdb_rating": "Rating IMDb", "count": "Frecuencia", "year_group": "Grupo de año"}
    )
    fig = style_fig(fig, height=360, show_legend=True, legend_position="bottom")
    st.plotly_chart(fig, use_container_width=True)

with bottom_right:
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