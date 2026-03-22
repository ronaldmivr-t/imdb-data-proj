import streamlit as st
import plotly.express as px
from utils import load_all_data, render_filters

st.title("Movies")

df, reviews_df = load_all_data()
filtered = render_filters(df)

c1, c2, c3 = st.columns(3)
c1.metric("Películas filtradas", len(filtered))
c2.metric("Rating máximo", round(filtered["imdb_rating"].max(), 2) if len(filtered) else 0)
c3.metric("Duración máxima", round(filtered["duration_minutes"].max(), 1) if len(filtered) else 0)

left, right = st.columns(2)

with left:
    fig = px.box(
        filtered,
        x="genre",
        y="imdb_rating",
        title="Distribución del rating por género"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.box(
        filtered,
        x="genre",
        y="duration_minutes",
        title="Distribución de duración por género"
    )
    st.plotly_chart(fig, use_container_width=True)

fig = px.scatter(
    filtered,
    x="duration_minutes",
    y="imdb_rating",
    color="genre",
    size="review_count",
    hover_data=["title", "year", "director"],
    title="Duración vs rating (tamaño = número de reseñas)"
)
st.plotly_chart(fig, use_container_width=True)

top_movies = filtered.sort_values("imdb_rating", ascending=False).head(10)
fig = px.bar(
    top_movies,
    x="title",
    y="imdb_rating",
    color="genre",
    title="Top 10 películas mejor calificadas"
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Tabla de películas")
show_cols = [
    "title", "genre", "year", "duration_minutes", "imdb_rating",
    "director", "review_count", "avg_sentiment_score"
]
st.dataframe(filtered[show_cols].sort_values("imdb_rating", ascending=False), use_container_width=True)