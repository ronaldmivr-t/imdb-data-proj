import streamlit as st
import plotly.express as px
from utils_json  import (
    load_all_data, render_filters, style_fig, style_bar_text, kpi_card,
    GENRE_COLORS, short_text, unique_movies
)

st.set_page_config(
    page_title="Películas",
    page_icon="🎬",
    layout="wide"
)

st.title("Películas")

df, reviews_df = load_all_data()
filtered = render_filters(df)

if filtered.empty:
    st.warning("No hay datos con los filtros actuales.")
    st.stop()

# Dataset sin duplicados por película
movies_unique = unique_movies(filtered)

# KPIs destacados
top_row = movies_unique.sort_values("imdb_rating", ascending=False).iloc[0]
bottom_row = movies_unique.sort_values("imdb_rating", ascending=True).iloc[0]
longest_row = movies_unique.sort_values("duration_minutes", ascending=False).iloc[0]

director_df = (
    movies_unique.groupby("director", as_index=False)["imdb_rating"]
    .mean()
    .dropna()
    .sort_values("imdb_rating", ascending=False)
)
best_director = director_df.iloc[0] if not director_df.empty else None

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        kpi_card("Mejor película", f"{top_row['imdb_rating']:.2f}", short_text(top_row["title"], 34)),
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        kpi_card("Película más baja", f"{bottom_row['imdb_rating']:.2f}", short_text(bottom_row["title"], 34)),
        unsafe_allow_html=True
    )
with c3:
    st.markdown(
        kpi_card(
            "Director destacado",
            f"{best_director['imdb_rating']:.2f}" if best_director is not None else "NA",
            short_text(best_director["director"], 34) if best_director is not None else ""
        ),
        unsafe_allow_html=True
    )
with c4:
    st.markdown(
        kpi_card("Película más larga", f"{longest_row['duration_minutes']:.0f} min", short_text(longest_row["title"], 34)),
        unsafe_allow_html=True
    )

left, right = st.columns(2)

with left:
    # Relación entre duración y rating IMDb
    fig = px.scatter(
        movies_unique,
        x="duration_minutes",
        y="imdb_rating",
        color="genre",
        size="avg_review_length",
        hover_data=["title", "year", "director"],
        color_discrete_sequence=GENRE_COLORS,
        title="Duración vs rating IMDb",
        labels={
            "duration_minutes": "Duración (min)",
            "imdb_rating": "Rating IMDb",
            "avg_review_length": "Longitud media de reseñas"
        }
    )
    fig = style_fig(fig, height=430, show_legend=True, legend_position="bottom")
    st.plotly_chart(fig, use_container_width=True)

with right:
    # Distribución del rating por género sin repetir películas
    fig = px.violin(
        movies_unique,
        x="genre",
        y="imdb_rating",
        color="genre",
        box=True,
        points="all",
        color_discrete_sequence=GENRE_COLORS,
        title="Comportamiento del rating por género",
        labels={"genre": "Género", "imdb_rating": "Rating IMDb"}
    )
    fig = style_fig(fig, height=430, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    # Tabla corta de top 10 mejores
    top10 = movies_unique.sort_values("imdb_rating", ascending=False).head(10).copy()
    top10["Película"] = top10["title"].apply(lambda x: short_text(x, 30))
    top10["Rating IMDb"] = top10["imdb_rating"].round(2)
    top10["Género"] = top10["genre"]
    top10["Director"] = top10["director"].apply(lambda x: short_text(x, 24))
    top10["#"] = range(1, len(top10) + 1)

    tabla_top = top10[["#", "Película", "Rating IMDb", "Género", "Director"]]

    st.markdown("### Top 10 mejor calificadas")
    st.dataframe(
        tabla_top,
        hide_index=True,
        use_container_width=True,
        height=390
    )

with bottom_right:
    # Ranking de películas con menor rating
    bottom10 = movies_unique.sort_values("imdb_rating", ascending=True).head(10).copy()
    bottom10["title_short"] = bottom10["title"].apply(lambda x: short_text(x, 28))

    fig = px.bar(
        bottom10.sort_values("imdb_rating", ascending=False),
        x="imdb_rating",
        y="title_short",
        orientation="h",
        color="genre",
        text="imdb_rating",
        color_discrete_sequence=GENRE_COLORS,
        title="Top 10 menor calificación",
        labels={"imdb_rating": "Rating IMDb", "title_short": "Película"}
    )
    fig = style_bar_text(fig, axis="x", size=16)
    fig = style_fig(fig, height=390, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)