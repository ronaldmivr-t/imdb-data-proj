import streamlit as st
import plotly.express as px
from utils_json  import (
    load_all_data, render_filters, style_fig, style_bar_text, kpi_card,
    GENRE_COLORS, SENTIMENT_COLORS, YEAR_COLORS, short_text, unique_movies
)

st.set_page_config(
    page_title="Sentimiento",
    page_icon="🎬",
    layout="wide"
)

st.title("Sentimiento")

df, reviews_df = load_all_data()
filtered_movies = render_filters(df)

if filtered_movies.empty:
    st.warning("No hay datos con los filtros actuales.")
    st.stop()

movie_ids = filtered_movies["movie_id"].tolist()
filtered_reviews = reviews_df[reviews_df["movie_id"].isin(movie_ids)].copy()

if filtered_reviews.empty:
    st.warning("No hay reseñas para los filtros actuales.")
    st.stop()

# Versión sin duplicados por película
movies_unique = unique_movies(filtered_movies)

pos_pct = round(filtered_reviews["sentiment_label"].eq("Positive").mean() * 100, 1)
neu_pct = round(filtered_reviews["sentiment_label"].eq("Neutral").mean() * 100, 1)
neg_pct = round(filtered_reviews["sentiment_label"].eq("Negative").mean() * 100, 1)

top_positive = movies_unique.sort_values("avg_sentiment_score", ascending=False).iloc[0]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("% positivas", f"{pos_pct}%", "Reseñas positivas"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("% neutras", f"{neu_pct}%", "Reseñas neutras"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("% negativas", f"{neg_pct}%", "Reseñas negativas"), unsafe_allow_html=True)
with c4:
    st.markdown(
        kpi_card("Película más positiva", f"{top_positive['avg_sentiment_score']:.2f}", short_text(top_positive["title"], 34)),
        unsafe_allow_html=True
    )

left, right = st.columns(2)

with left:
    sentiment_counts = filtered_reviews["sentiment_label"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]

    fig = px.pie(
        sentiment_counts,
        names="sentiment",
        values="count",
        hole=0.6,
        color="sentiment",
        color_discrete_map=SENTIMENT_COLORS,
        title="Distribución global del sentimiento"
    )
    fig = style_fig(fig, height=390, show_legend=True, legend_position="bottom")
    st.plotly_chart(fig, use_container_width=True)

with right:
    year_sent = (
        movies_unique.groupby("year_group", as_index=False)["avg_sentiment_score"]
        .mean()
        .dropna()
    )

    fig = px.bar(
        year_sent,
        x="year_group",
        y="avg_sentiment_score",
        text="avg_sentiment_score",
        color="year_group",
        color_discrete_sequence=YEAR_COLORS,
        title="Sentimiento promedio por grupo de año",
        labels={"year_group": "Grupo de año", "avg_sentiment_score": "Sentimiento promedio"}
    )
    fig = style_bar_text(fig, axis="y", size=16)
    fig = style_fig(fig, height=390, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    fig = px.scatter(
        movies_unique,
        x="imdb_rating",
        y="avg_sentiment_score",
        color="genre",
        size="avg_review_length",
        hover_data=["title", "year"],
        color_discrete_sequence=GENRE_COLORS,
        title="Rating IMDb vs sentimiento promedio",
        labels={
            "imdb_rating": "Rating IMDb",
            "avg_sentiment_score": "Sentimiento promedio",
            "avg_review_length": "Longitud media"
        }
    )
    fig = style_fig(fig, height=390, show_legend=True, legend_position="bottom")
    st.plotly_chart(fig, use_container_width=True)

with bottom_right:
    # Tabla corta de las películas con sentimiento promedio más positivo
    top_pos = movies_unique.sort_values("avg_sentiment_score", ascending=False).head(10).copy()
    top_pos["#"] = range(1, len(top_pos) + 1)
    top_pos["Película"] = top_pos["title"].apply(lambda x: short_text(x, 34))
    top_pos["Sentimiento"] = top_pos["avg_sentiment_score"].round(3)
    top_pos["Género"] = top_pos["genre"]
    top_pos["Rating IMDb"] = top_pos["imdb_rating"].round(2)

    tabla_pos = top_pos[["#", "Película", "Sentimiento", "Género", "Rating IMDb"]]

    st.markdown("### Top 10 películas más positivas")
    st.dataframe(
        tabla_pos,
        hide_index=True,
        use_container_width=True,
        height=390
    )