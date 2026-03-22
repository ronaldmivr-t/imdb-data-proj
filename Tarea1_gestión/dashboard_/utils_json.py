import re
import json
import os
import pandas as pd
import streamlit as st
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# CONSTANTS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_JSON_PATH = os.path.join(BASE_DIR, "movie.json")

# =========================
# Sentimiento
# =========================

@st.cache_resource
def get_sia():
    nltk.download("vader_lexicon", quiet=True)
    return SentimentIntensityAnalyzer()

def sentiment_label(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    return "Neutral"

# =========================
# Limpieza y normalización
# =========================

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
    m_match = re.search(r"(\d+)\s*min", text) or re.search(r"(\d+)\s*m", text)

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

def normalize_cast(cast_value):
    if isinstance(cast_value, list):
        clean = [str(x).strip() for x in cast_value if str(x).strip()]
        return ", ".join(clean)
    if pd.isna(cast_value):
        return ""
    return str(cast_value).strip()

def extract_review_rating(review_item):
    if isinstance(review_item, list) and len(review_item) > 0:
        return normalize_rating(review_item[0])
    return None

def extract_review_text(review_item):
    """
    Convierte cada reseña del JSON a un texto único.
    La estructura del JSON mezcla rating, '/10', título corto y cuerpo.
    """
    if isinstance(review_item, list):
        parts = []
        for i, x in enumerate(review_item):
            x = str(x).strip()
            if not x:
                continue
            if x == "/10":
                continue
            # saltar el rating numérico del primer campo
            if i == 0 and normalize_rating(x) is not None:
                continue
            # dejar spoilers fuera del texto analítico
            if x.lower() == "spoiler":
                continue
            parts.append(x)
        return " ".join(parts).strip()

    return str(review_item).strip()

# =========================
# Lectura del JSON
# =========================

@st.cache_data
def load_raw_json(json_path=DEFAULT_JSON_PATH):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_movies(json_path=DEFAULT_JSON_PATH):
    raw = load_raw_json(json_path)

    rows = []
    for idx, item in enumerate(raw, start=1):
        rows.append({
            "movie_id": idx,
            "title": item.get("Titulo"),
            "genre": item.get("Género"),
            "year": normalize_rating(item.get("Año")),
            "duration_raw": item.get("Duración"),
            "imdb_rating": normalize_rating(item.get("Calificación")),
            "director": item.get("Director"),
            "cast": normalize_cast(item.get("Protagonistas")),
            "synopsis": item.get("Sinopsis")
        })

    df = pd.DataFrame(rows)
    df["duration_minutes"] = df["duration_raw"].apply(convert_duration_to_minutes)
    return df

@st.cache_data
def load_reviews(json_path=DEFAULT_JSON_PATH):
    raw = load_raw_json(json_path)

    rows = []
    review_id = 1

    for idx, item in enumerate(raw, start=1):
        reviews = item.get("Reseñas", [])
        for review in reviews:
            rows.append({
                "review_id": review_id,
                "movie_id": idx,
                "review_text": extract_review_text(review),
                "review_rating": extract_review_rating(review)
            })
            review_id += 1

    df = pd.DataFrame(rows)

    if df.empty:
        df = pd.DataFrame(columns=["review_id", "movie_id", "review_text", "review_rating"])

    df["review_text"] = df["review_text"].fillna("").astype(str).str.strip()
    df["review_rating"] = df["review_rating"].apply(normalize_rating)
    df["review_length_words"] = df["review_text"].str.split().str.len()

    sia = get_sia()
    df["sentiment_score"] = df["review_text"].apply(
        lambda x: sia.polarity_scores(x)["compound"] if x else 0
    )
    df["sentiment_label"] = df["sentiment_score"].apply(sentiment_label)

    return df

# =========================
# Dataset analítico
# =========================

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
def load_all_data(json_path=DEFAULT_JSON_PATH):
    movies = load_movies(json_path)
    reviews = load_reviews(json_path)
    dashboard_df = build_movie_dashboard_df(movies, reviews)
    return dashboard_df, reviews

# =========================
# Filtros
# =========================

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

# =========================
# Helpers del dashboard
# =========================

GENRE_COLORS = ["#6366F1", "#06B6D4", "#22C55E", "#F59E0B", "#EF4444", "#A855F7"]
SENTIMENT_COLORS = {
    "Positive": "#22C55E",
    "Neutral": "#94A3B8",
    "Negative": "#EF4444"
}
YEAR_COLORS = ["#3B82F6", "#6366F1", "#8B5CF6", "#14B8A6", "#F59E0B"]
RATING_BAND_COLORS = ["#1D4ED8", "#0EA5E9", "#10B981", "#F97316"]

def short_text(text, max_len=32):
    if text is None:
        return ""
    text = str(text)
    return text if len(text) <= max_len else text[:max_len - 3] + "..."

def unique_movies(df):
    temp = df.copy()
    temp["title_clean"] = temp["title"].astype(str).str.strip()
    temp["movie_key"] = temp["title_clean"] + " | " + temp["year"].astype("Int64").astype(str)

    temp = temp.sort_values(
        by=["movie_key", "imdb_rating", "avg_review_length"],
        ascending=[True, False, False]
    )
    temp = temp.drop_duplicates(subset=["movie_key"], keep="first").copy()
    return temp

def kpi_card(title, value, subtitle=""):
    return f"""
    <div style="
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        min-height: 120px;
    ">
        <div style="font-size: 0.95rem; color: #475569; margin-bottom: 0.5rem; font-weight: 600;">
            {title}
        </div>
        <div style="font-size: 1.8rem; color: #0F172A; font-weight: 800; line-height: 1.1;">
            {value}
        </div>
        <div style="font-size: 0.88rem; color: #64748B; margin-top: 0.55rem;">
            {subtitle}
        </div>
    </div>
    """

def style_fig(fig, height=380, show_legend=True, legend_position="bottom"):
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=85, b=70 if show_legend and legend_position == "bottom" else 25),
        font=dict(family="Arial", size=13, color="#0F172A"),
        title=dict(x=0.02, y=0.97, xanchor="left", yanchor="top", font=dict(size=18, color="#0F172A")),
        showlegend=show_legend
    )

    if show_legend:
        if legend_position == "bottom":
            fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.20,
                    xanchor="center",
                    x=0.5
                )
            )
        elif legend_position == "right":
            fig.update_layout(
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                )
            )

    fig.update_xaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)
    return fig

def style_bar_text(fig, axis="x", size=16):
    texttemplate = "%{x:.2f}" if axis == "x" else "%{y:.2f}"
    fig.update_traces(
        texttemplate=texttemplate,
        textposition="outside",
        textfont_size=size,
        cliponaxis=False
    )
    fig.update_layout(
        uniformtext_minsize=max(size - 2, 10),
        uniformtext_mode="hide"
    )
    return fig
