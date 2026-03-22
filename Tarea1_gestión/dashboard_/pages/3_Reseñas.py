import streamlit as st
import plotly.express as px
from utils_json import (
    load_all_data,
    render_filters,
    style_fig,
    style_bar_text,
    kpi_card,
    GENRE_COLORS,
    short_text,
    unique_movies,
    make_binned_bar_by_group
)

st.set_page_config(
    page_title="Reseñas",
    page_icon="🎬",
    layout="wide"
)

st.title("Reseñas")

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

# Dataset comparativo entre rating IMDb y rating medio de reseñas
comparison_df = movies_unique.copy()
comparison_df["rating_gap"] = (
    comparison_df["imdb_rating"] - comparison_df["avg_review_rating"]
).abs()

# =========================
# KPIs
# =========================
avg_review_len = round(filtered_reviews["review_length_words"].mean(), 1)
avg_review_rating = round(filtered_reviews["review_rating"].mean(), 2) if filtered_reviews["review_rating"].notna().any() else 0
avg_gap = round(comparison_df["rating_gap"].mean(), 2)

longest_review_movie = (
    comparison_df.sort_values("avg_review_length", ascending=False).iloc[0]
    if comparison_df["avg_review_length"].notna().any()
    else None
)

max_gap_movie = (
    comparison_df.sort_values("rating_gap", ascending=False).iloc[0]
    if comparison_df["rating_gap"].notna().any()
    else None
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        kpi_card("Longitud media", f"{avg_review_len} palabras", "Promedio por reseña"),
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        kpi_card("Rating medio reseñas", avg_review_rating, "Promedio de usuarios"),
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        kpi_card(
            "Mayor brecha IMDb-reseñas",
            f"{max_gap_movie['rating_gap']:.2f}" if max_gap_movie is not None else "NA",
            short_text(max_gap_movie["title"], 34) if max_gap_movie is not None else ""
        ),
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        kpi_card(
            "Reseñas más extensas",
            f"{longest_review_movie['avg_review_length']:.1f}" if longest_review_movie is not None else "NA",
            short_text(longest_review_movie["title"], 34) if longest_review_movie is not None else ""
        ),
        unsafe_allow_html=True
    )

left, right = st.columns(2)

with left:
    # Gráfico 1:
    # Reemplaza el histograma por barras agrupadas.
    # Muestra la distribución de la longitud de las reseñas segmentada por sentimiento.
    fig = make_binned_bar_by_group(
        df=filtered_reviews,
        column="review_length_words",
        group_col="sentiment_label",
        bins=[0, 25, 50, 75, 100, 150, 200, 500],
        labels=["0-25", "26-50", "51-75", "76-100", "101-150", "151-200", "200+"],
        title="Distribución de longitud de reseñas",
        x_label="Palabras por reseña",
        group_label="Sentimiento",
        color_sequence=["#22C55E", "#94A3B8", "#EF4444"],
        barmode="group"
    )
    fig = style_fig(fig, height=390, show_legend=True, legend_position="bottom")
    st.plotly_chart(fig, use_container_width=True)

with right:
    # Gráfico 2:
    # Compara la longitud de las reseñas entre géneros.
    reviews_with_genre = filtered_reviews.merge(
        movies_unique[["movie_id", "genre"]],
        on="movie_id",
        how="left"
    )

    fig = px.box(
        reviews_with_genre,
        x="genre",
        y="review_length_words",
        color="genre",
        color_discrete_sequence=GENRE_COLORS,
        title="Longitud de reseñas por género",
        labels={
            "genre": "Género",
            "review_length_words": "Palabras por reseña"
        }
    )
    fig = style_fig(fig, height=390, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    # Gráfico 3:
    # Relaciona el rating IMDb con el rating medio de las reseñas.
    # La línea punteada representa coincidencia perfecta.
    scatter_df = comparison_df.dropna(subset=["imdb_rating", "avg_review_rating"]).copy()

    fig = px.scatter(
        scatter_df,
        x="imdb_rating",
        y="avg_review_rating",
        color="genre",
        size="avg_review_length",
        hover_data=["title", "year"],
        color_discrete_sequence=GENRE_COLORS,
        title="IMDb vs rating medio de reseñas",
        labels={
            "imdb_rating": "Rating IMDb",
            "avg_review_rating": "Rating medio reseñas",
            "avg_review_length": "Longitud media"
        }
    )

    if not scatter_df.empty:
        min_val = min(scatter_df["imdb_rating"].min(), scatter_df["avg_review_rating"].min())
        max_val = max(scatter_df["imdb_rating"].max(), scatter_df["avg_review_rating"].max())

        fig.add_shape(
            type="line",
            x0=min_val,
            y0=min_val,
            x1=max_val,
            y1=max_val,
            line=dict(color="#94A3B8", dash="dash")
        )

    fig = style_fig(fig, height=390, show_legend=True, legend_position="bottom")
    st.plotly_chart(fig, use_container_width=True)

with bottom_right:
    # Gráfico 4:
    # Muestra qué películas tienen mayor diferencia entre rating IMDb
    # y rating medio calculado a partir de las reseñas.
    gap_movies = comparison_df.sort_values("rating_gap", ascending=False).head(10).copy()
    gap_movies["title_short"] = gap_movies["title"].apply(lambda x: short_text(x, 28))

    fig = px.bar(
        gap_movies.sort_values("rating_gap", ascending=True),
        x="rating_gap",
        y="title_short",
        orientation="h",
        color="genre",
        text="rating_gap",
        color_discrete_sequence=GENRE_COLORS,
        title="Mayor diferencia entre IMDb y reseñas",
        labels={
            "rating_gap": "Diferencia absoluta",
            "title_short": "Película"
        }
    )
    fig = style_bar_text(fig, axis="x", size=16)
    fig = style_fig(fig, height=390, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)