import streamlit as st
import plotly.express as px
from utils import load_all_data, render_filters

st.title("Overview")

df, reviews_df = load_all_data()
filtered = render_filters(df)

total_movies = len(filtered)
total_genres = filtered["genre"].nunique()
avg_rating = round(filtered["imdb_rating"].mean(), 2) if total_movies > 0 else 0
avg_duration = round(filtered["duration_minutes"].mean(), 1) if total_movies > 0 else 0
total_reviews = int(filtered["review_count"].sum()) if total_movies > 0 else 0
movies_before_2010 = int((filtered["year"] <= 2009).sum())
movies_after_2022 = int((filtered["year"] >= 2023).sum())

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Películas", total_movies)
c2.metric("Géneros", total_genres)
c3.metric("Rating medio", avg_rating)
c4.metric("Duración media", avg_duration)
c5.metric("Reseñas", total_reviews)
c6.metric("Películas 2023+", movies_after_2022)

left, right = st.columns(2)

with left:
    count_by_genre = filtered.groupby("genre", as_index=False).size().rename(columns={"size": "movie_count"})
    fig = px.bar(
        count_by_genre,
        x="genre",
        y="movie_count",
        title="Cantidad de películas por género"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    avg_rating_genre = filtered.groupby("genre", as_index=False)["imdb_rating"].mean()
    fig = px.bar(
        avg_rating_genre,
        x="genre",
        y="imdb_rating",
        title="Rating promedio por género"
    )
    st.plotly_chart(fig, use_container_width=True)

year_group_df = filtered.groupby("year_group", as_index=False).size().rename(columns={"size": "movie_count"})
fig = px.bar(
    year_group_df,
    x="year_group",
    y="movie_count",
    title="Películas por grupo de año"
)
st.plotly_chart(fig, use_container_width=True)

st.markdown(f"""
**Lectura rápida**
- Películas antiguas (<= 2009): **{movies_before_2010}**
- Películas recientes (2023+): **{movies_after_2022}**
""")