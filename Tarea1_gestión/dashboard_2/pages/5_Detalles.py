import streamlit as st
import plotly.express as px
from utils_json import (
    load_all_data,
    render_filters,
    style_fig,
    kpi_card,
    SENTIMENT_COLORS,
    short_text,
    unique_movies,
    make_binned_bar
)

st.set_page_config(
    page_title="Detalle película",
    page_icon="🎬",
    layout="wide"
)

st.title("Detalle película")

df, reviews_df = load_all_data()
filtered = render_filters(df)

if filtered.empty:
    st.warning("No hay películas con los filtros actuales.")
    st.stop()

# Dataset sin duplicados por película
movies_unique = unique_movies(filtered)

selected_title = st.selectbox(
    "Selecciona una película",
    sorted(movies_unique["title"].unique())
)

movie = movies_unique[movies_unique["title"] == selected_title].iloc[0]
movie_reviews = reviews_df[reviews_df["movie_id"] == movie["movie_id"]].copy()

# =========================
# KPIs
# =========================
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        kpi_card("Rating IMDb", f"{movie['imdb_rating']:.2f}", short_text(movie["title"], 32)),
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        kpi_card("Duración", f"{movie['duration_minutes']:.0f} min", movie["genre"]),
        unsafe_allow_html=True
    )
with c3:
    st.markdown(
        kpi_card("Rating reseñas", f"{movie['avg_review_rating']:.2f}", f"Año: {int(movie['year'])}"),
        unsafe_allow_html=True
    )
with c4:
    st.markdown(
        kpi_card("Sentimiento", f"{movie['avg_sentiment_score']:.2f}", movie["dominant_sentiment"]),
        unsafe_allow_html=True
    )

left, right = st.columns([1.1, 1])

with left:
    # Tarjeta descriptiva de la película
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid #E2E8F0; border-radius: 16px; padding: 18px; box-shadow: 0 4px 14px rgba(15,23,42,0.05);'>
        <div style='font-size: 1.5rem; font-weight: 800; color: #0F172A; margin-bottom: 0.6rem;'>
            {movie["title"]}
        </div>
        <div style='color: #475569; margin-bottom: 0.3rem;'><b>Director:</b> {movie["director"]}</div>
        <div style='color: #475569; margin-bottom: 0.3rem;'><b>Protagonistas:</b> {movie["cast"]}</div>
        <div style='color: #475569; margin-bottom: 0.9rem;'><b>Género:</b> {movie["genre"]}</div>
        <div style='color: #0F172A;'><b>Sinopsis</b></div>
        <div style='color: #475569; margin-top: 0.35rem;'>{movie["synopsis"]}</div>
    </div>
    """, unsafe_allow_html=True)

with right:
    if not movie_reviews.empty:
        # Gráfico 1:
        # Muestra la composición del sentimiento de las reseñas de esta película.
        sentiment_counts = movie_reviews["sentiment_label"].value_counts().reset_index()
        sentiment_counts.columns = ["sentiment", "count"]

        fig = px.pie(
            sentiment_counts,
            names="sentiment",
            values="count",
            hole=0.62,
            color="sentiment",
            color_discrete_map=SENTIMENT_COLORS,
            title="Sentimiento de sus reseñas"
        )
        fig = style_fig(fig, height=320, show_legend=True, legend_position="bottom")
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico 2:
        # Reemplaza el histograma por barras para el rating de reseñas.
        if movie_reviews["review_rating"].notna().any():
            fig = make_binned_bar(
                df=movie_reviews,
                column="review_rating",
                bins=[0, 2, 4, 6, 8, 10],
                labels=["0-2", "2-4", "4-6", "6-8", "8-10"],
                title="Distribución del rating de reseñas",
                x_label="Rango rating reseñas",
                color_sequence=["#93C5FD", "#60A5FA", "#2563EB", "#1D4ED8", "#1E3A8A"]
            )
            fig = style_fig(fig, height=260, show_legend=False)
            st.plotly_chart(fig, use_container_width=True)

if not movie_reviews.empty:
    # Tarjetas de reseñas destacadas
    top_reviews = (
        movie_reviews.assign(review_preview=movie_reviews["review_text"].str.slice(0, 170) + "...")
        .sort_values("sentiment_score", ascending=False)
        .head(3)
    )

    st.markdown("### Reseñas destacadas")
    cols = st.columns(3)
    for i, (_, row) in enumerate(top_reviews.iterrows()):
        with cols[i]:
            st.markdown(f"""
            <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 14px; min-height: 220px; box-shadow: 0 4px 12px rgba(15,23,42,0.04);'>
                <div style='font-size: 0.88rem; color: #64748B; margin-bottom: 0.5rem;'>
                    {row["sentiment_label"]} | Rating: {row["review_rating"]}
                </div>
                <div style='font-size: 0.95rem; color: #334155;'>
                    {row["review_preview"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Esta película no tiene reseñas registradas.")