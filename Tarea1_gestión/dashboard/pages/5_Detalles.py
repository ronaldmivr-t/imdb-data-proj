import streamlit as st
from utils import load_all_data, render_filters

st.title("Movie Detail")

df, reviews_df = load_all_data()
filtered = render_filters(df)

titles = sorted(filtered["title"].dropna().unique().tolist())

if not titles:
    st.warning("No hay películas con los filtros actuales.")
else:
    selected_title = st.selectbox("Selecciona una película", titles)
    movie = filtered[filtered["title"] == selected_title].iloc[0]

    c1, c2 = st.columns([1, 2])

    with c1:
        st.metric("IMDb rating", round(movie["imdb_rating"], 2) if movie["imdb_rating"] else 0)
        st.metric("Duración", round(movie["duration_minutes"], 1) if movie["duration_minutes"] else 0)
        st.metric("Reseñas", int(movie["review_count"]))
        st.metric("Sentimiento medio", round(movie["avg_sentiment_score"], 3))

    with c2:
        st.subheader(movie["title"])
        st.write(f"**Género:** {movie['genre']}")
        st.write(f"**Año:** {int(movie['year']) if movie['year'] == movie['year'] else 'NA'}")
        st.write(f"**Director:** {movie['director']}")
        st.write(f"**Protagonistas:** {movie['cast']}")
        st.write(f"**Sentimiento dominante:** {movie['dominant_sentiment']}")
        st.write("**Sinopsis:**")
        st.write(movie["synopsis"])

    st.subheader("Reseñas de esta película")
    movie_reviews = reviews_df[reviews_df["movie_id"] == movie["movie_id"]].copy()

    if movie_reviews.empty:
        st.info("Esta película no tiene reseñas en la tabla de reviews.")
    else:
        st.dataframe(
            movie_reviews[["review_text", "review_rating", "review_length_words", "sentiment_score", "sentiment_label"]],
            use_container_width=True
        )