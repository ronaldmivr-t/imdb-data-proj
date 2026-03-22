import streamlit as st
import plotly.express as px
from utils import load_all_data, render_filters

st.title("Sentiment")

df, reviews_df = load_all_data()
filtered_movies = render_filters(df)

movie_ids = filtered_movies["movie_id"].tolist()
filtered_reviews = reviews_df[reviews_df["movie_id"].isin(movie_ids)].copy()

sentiment_counts = filtered_reviews["sentiment_label"].value_counts().reset_index()
sentiment_counts.columns = ["sentiment", "count"]

c1, c2, c3 = st.columns(3)
c1.metric("Positive", int((filtered_reviews["sentiment_label"] == "Positive").sum()))
c2.metric("Neutral", int((filtered_reviews["sentiment_label"] == "Neutral").sum()))
c3.metric("Negative", int((filtered_reviews["sentiment_label"] == "Negative").sum()))

left, right = st.columns(2)

with left:
    fig = px.pie(
        sentiment_counts,
        names="sentiment",
        values="count",
        hole=0.5,
        title="Composición general del sentimiento"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    sentiment_by_genre = filtered_movies.groupby("genre", as_index=False)["avg_sentiment_score"].mean()
    fig = px.bar(
        sentiment_by_genre,
        x="genre",
        y="avg_sentiment_score",
        title="Sentimiento promedio por género"
    )
    st.plotly_chart(fig, use_container_width=True)

genre_label_counts = filtered_reviews.merge(
    filtered_movies[["movie_id", "genre"]],
    on="movie_id",
    how="left"
).groupby(["genre", "sentiment_label"], as_index=False).size().rename(columns={"size": "count"})

fig = px.bar(
    genre_label_counts,
    x="genre",
    y="count",
    color="sentiment_label",
    barmode="group",
    title="Sentimiento por género"
)
st.plotly_chart(fig, use_container_width=True)

heatmap_df = filtered_movies.groupby(["genre", "rating_band"], as_index=False)["avg_sentiment_score"].mean()
heatmap_pivot = heatmap_df.pivot(index="genre", columns="rating_band", values="avg_sentiment_score")

fig = px.imshow(
    heatmap_pivot,
    text_auto=True,
    aspect="auto",
    title="Heatmap: sentimiento promedio por género y banda de rating"
)
st.plotly_chart(fig, use_container_width=True)