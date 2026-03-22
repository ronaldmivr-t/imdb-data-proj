import re
import pandas as pd
import streamlit as st
import nltk

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from db import query_to_df

@st.cache_resource
def get_sia():
    nltk.download("vader_lexicon", quiet=True)
    return SentimentIntensityAnalyzer()

def convert_duration_to_minutes(duration_value):
    if pd.isna(duration_value):
        return None

    if isinstance(duration_value, (int, float)):
        return float(duration_value)

    text = str(duration_value).strip().lower()

    if text.isdigit():
        return float(text)

    hours = 0
    minutes = 0

    h_match = re.search(r"(\d+)\s*h", text)
    m_match = re.search(r"(\d+)\s*m", text)

    if h_match:
        hours = int(h_match.group(1))
    if m_match:
        minutes = int(m_match.group(1))

    total = hours * 60 + minutes
    return float(total) if total > 0 else None

def normalize_rating(value):
    if pd.isna(value):
        return None
    text = str(value).replace(",", ".").strip()
    return pd.to_numeric(text, errors="coerce")

def sentiment_label(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    return "Neutral"

@st.cache_data
def load_movies():
    query = """
    SELECT
        IDTITULO AS movie_id,
        TITULO AS title,
        GENERO AS genre,
        ANO AS year,
        DURACION AS duration_raw,
        CALIFICACION AS imdb_rating,
        DIRECTOR AS director,
        PROTAGONISTAS AS cast,
        SINOPSIS AS synopsis
    FROM PELICULA
    """
    df = query_to_df(query)

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["imdb_rating"] = df["imdb_rating"].apply(normalize_rating)
    df["duration_minutes"] = df["duration_raw"].apply(convert_duration_to_minutes)

    return df

@st.cache_data
def load_reviews():
    query = """
    SELECT
        IDREVIEW AS review_id,
        IDTITULO AS movie_id,
        REVIEW AS review_text,
        CALIFICACION AS review_rating
    FROM REVIEW
    """
    df = query_to_df(query)

    df["review_text"] = df["review_text"].fillna("").astype(str).str.strip()
    df["review_rating"] = df["review_rating"].apply(normalize_rating)
    df["review_length_words"] = df["review_text"].str.split().str.len()

    sia = get_sia()
    df["sentiment_score"] = df["review_text"].apply(
        lambda x: sia.polarity_scores(x)["compound"] if x else 0
    )
    df["sentiment_label"] = df["sentiment_score"].apply(sentiment_label)

    return df

def build_movie_dashboard_df(movies_df, reviews_df):
    reviews_agg = reviews_df.groupby("movie_id", as_index=False).agg(
        review_count=("review_id", "count"),
        avg_review_rating=("review_rating", "mean"),
        avg_review_length=("review_length_words", "mean"),
        avg_sentiment_score=("sentiment_score", "mean"),
        positive_reviews=("sentiment_label", lambda s: (s == "Positive").sum()),
        neutral_reviews=("sentiment_label", lambda s: (s == "Neutral").sum()),
        negative_reviews=("sentiment_label", lambda s: (s == "Negative").sum())
    )

    merged = movies_df.merge(reviews_agg, on="movie_id", how="left")

    numeric_cols = [
        "review_count", "avg_review_rating", "avg_review_length",
        "avg_sentiment_score", "positive_reviews", "neutral_reviews", "negative_reviews"
    ]

    for col in numeric_cols:
        merged[col] = merged[col].fillna(0)

    def dominant_sentiment(row):
        scores = {
            "Positive": row["positive_reviews"],
            "Neutral": row["neutral_reviews"],
            "Negative": row["negative_reviews"]
        }
        return max(scores, key=scores.get)

    merged["dominant_sentiment"] = merged.apply(dominant_sentiment, axis=1)

    merged["year_group"] = pd.cut(
        merged["year"],
        bins=[1900, 2009, 2019, 2022, 2024, 2100],
        labels=["<=2009", "2010-2019", "2020-2022", "2023-2024", "2025+"]
    )

    merged["rating_band"] = pd.cut(
        merged["imdb_rating"],
        bins=[0, 6.4, 7.4, 8.4, 10],
        labels=["<=6.4", "6.5-7.4", "7.5-8.4", "8.5+"],
        include_lowest=True
    )

    return merged

@st.cache_data
def load_all_data():
    movies = load_movies()
    reviews = load_reviews()
    dashboard_df = build_movie_dashboard_df(movies, reviews)
    return dashboard_df, reviews

def render_filters(df):
    st.sidebar.header("Filtros")

    genres = sorted(df["genre"].dropna().unique().tolist())
    directors = sorted(df["director"].dropna().unique().tolist())

    selected_genres = st.sidebar.multiselect("Género", genres, default=genres)

    year_min = int(df["year"].min()) if df["year"].notna().any() else 2000
    year_max = int(df["year"].max()) if df["year"].notna().any() else 2024
    selected_years = st.sidebar.slider("Rango de años", year_min, year_max, (year_min, year_max))

    selected_rating = st.sidebar.slider("Rango rating IMDb", 0.0, 10.0, (0.0, 10.0), 0.1)

    selected_directors = st.sidebar.multiselect("Director", directors)

    filtered = df.copy()

    filtered = filtered[filtered["genre"].isin(selected_genres)]
    filtered = filtered[
        (filtered["year"] >= selected_years[0]) &
        (filtered["year"] <= selected_years[1])
    ]
    filtered = filtered[
        (filtered["imdb_rating"] >= selected_rating[0]) &
        (filtered["imdb_rating"] <= selected_rating[1])
    ]

    if selected_directors:
        filtered = filtered[filtered["director"].isin(selected_directors)]

    return filtered