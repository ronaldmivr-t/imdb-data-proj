import streamlit as st
import plotly.express as px
from utils import load_all_data, render_filters

st.title("Reviews")

df, reviews_df = load_all_data()
filtered_movies = render_filters(df)

movie_ids = filtered_movies["movie_id"].tolist()
filtered_reviews = reviews_df[reviews_df["movie_id"].isin(movie_ids)].copy()

c1, c2, c3 = st.columns(3)
c1.metric("Reseñas filtradas", len(filtered_reviews))
c2.metric("Longitud media reseña", round(filtered_reviews["review_length_words"].mean(), 1) if len(filtered_reviews) else 0)
c3.metric("Sentimiento medio", round(filtered_reviews["sentiment_score"].mean(), 3) if len(filtered_reviews) else 0)

reviews_per_genre = filtered_movies.groupby("genre", as_index=False)["review_count"].sum()
fig = px.bar(
    reviews_per_genre,
    x="genre",
    y="review_count",
    title="Número total de reseñas por género"
)
st.plotly_chart(fig, use_container_width=True)

genre_review_length = filtered_movies.groupby("genre", as_index=False)["avg_review_length"].mean()
fig = px.bar(
    genre_review_length,
    x="genre",
    y="avg_review_length",
    title="Longitud media de reseña por género"
)
st.plotly_chart(fig, use_container_width=True)

top_reviewed = filtered_movies.sort_values("review_count", ascending=False).head(10)
fig = px.bar(
    top_reviewed,
    x="title",
    y="review_count",
    color="genre",
    title="Top 10 películas con más reseñas"
)
st.plotly_chart(fig, use_container_width=True)

if "review_rating" in filtered_reviews.columns and filtered_reviews["review_rating"].notna().any():
    fig = px.histogram(
        filtered_reviews,
        x="review_rating",
        nbins=10,
        title="Distribución del rating de reseñas"
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Detalle de reseñas")
st.dataframe(
    filtered_reviews[["movie_id", "review_id", "review_text", "review_rating", "review_length_words", "sentiment_label"]].head(100),
    use_container_width=True
)