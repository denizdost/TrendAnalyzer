import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

DISCOUNT_FAKE_THRESHOLD = 0.15
BEST_BUY_SCORE_THRESHOLD = 70
FAIR_SCORE_THRESHOLD = 40

# Simple Turkish sentiment word lists
POSITIVE_WORDS = [
    "iyi", "güzel", "harika", "mükemmel", "süper", "kaliteli", "beğendim",
    "memnun", "tavsiye", "sevdim", "hızlı", "sağlam", "şık", "başarılı",
    "kusursuz", "muhteşem", "teşekkür", "aldım", "aldik", "ideal", "rahat",
    "ucuz", "uygun", "değer", "gerçek", "doğru", "tam", "mükemmeldi"
]
NEGATIVE_WORDS = [
    "kötü", "berbat", "rezalet", "bozuk", "sahte", "yalan", "aldatmaca",
    "kalitesiz", "beğenmedim", "iade", "şikayet", "geç", "gelmedi", "kırık",
    "işe yaramaz", "pişman", "dolandırıcı", "çöp", "sorun", "hata", "eksik",
    "yanlış", "hayal kırıklığı", "tavsiye etmem", "aldatıldım", "sahte"
]


def load_data():
    products = pd.read_csv("data/products.csv")
    sellers = pd.read_csv("data/sellers.csv")
    reviews = pd.read_csv("data/reviews.csv")
    prices = pd.read_csv("data/prices.csv")
    return products, sellers, reviews, prices


def preprocess(products, sellers):
    Q1 = products["discounted_price"].quantile(0.25)
    Q3 = products["discounted_price"].quantile(0.75)
    IQR = Q3 - Q1
    products = products[
        (products["discounted_price"] >= Q1 - 1.5 * IQR) &
        (products["discounted_price"] <= Q3 + 1.5 * IQR)
    ].copy()
    products = products.dropna()
    return products, sellers


def analyze_sentiment(text):
    """Rule-based Turkish sentiment analysis."""
    if not isinstance(text, str):
        return "Nötr"
    text_lower = text.lower()
    pos_score = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg_score = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    if pos_score > neg_score:
        return "Pozitif"
    elif neg_score > pos_score:
        return "Negatif"
    else:
        return "Nötr"


def apply_sentiment_to_reviews(reviews):
    """Apply sentiment analysis to all reviews."""
    reviews = reviews.copy()
    reviews["sentiment"] = reviews["text"].apply(analyze_sentiment)
    return reviews


def calculate_performance_score(products, sellers):
    sellers_renamed = sellers.rename(
        columns={"name": "seller_name", "rating": "seller_rating"}
    )
    merged = products.merge(sellers_renamed, on="seller_id", how="left")

    merged["rating_score"] = (merged["rating"] / 5.0) * 40
    max_log = np.log1p(merged["review_count"].max())
    merged["review_score"] = (np.log1p(merged["review_count"]) / max_log) * 30
    merged["trust_score"] = (merged["seller_rating"] / 5.0) * 30

    merged["performance_score"] = (
        merged["rating_score"] + merged["review_score"] + merged["trust_score"]
    ).round(1)
    return merged


def apply_kmeans_clustering(scored):
    """Real KMeans clustering on price, performance_score, review_count."""
    df = scored.copy()
    features = df[["discounted_price", "performance_score", "review_count"]].copy()

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(scaled)

    # Map clusters to labels based on centroid performance score
    centroids = pd.DataFrame(
        scaler.inverse_transform(kmeans.cluster_centers_),
        columns=["discounted_price", "performance_score", "review_count"]
    )
    sorted_clusters = centroids["performance_score"].rank(ascending=False)
    label_map = {}
    for cluster_id, rank in sorted_clusters.items():
        if rank == 1:
            label_map[cluster_id] = "🏆 Best Buy"
        elif rank == 2:
            label_map[cluster_id] = "✅ Fair Value"
        else:
            label_map[cluster_id] = "⚠️ Overpriced"

    df["cluster_label"] = df["cluster"].map(label_map)
    return df


def verify_discount(products):
    df = products.copy()
    df["discount_gap"] = df["claimed_discount_rate"] - df["real_discount_rate"]
    df["is_fake_discount"] = df["discount_gap"] > DISCOUNT_FAKE_THRESHOLD
    df["discount_verdict"] = df["is_fake_discount"].map({
        True: "❌ Yanıltıcı",
        False: "✅ Gerçek"
    })
    return df


def seller_trust_analysis(sellers, reviews):
    sentiment_scores = reviews.groupby("seller_id").apply(
        lambda x: (x["sentiment"] == "Pozitif").sum() / len(x) * 100
    ).reset_index(name="positive_rate")

    merged = sellers.merge(sentiment_scores, on="seller_id", how="left")
    merged["positive_rate"] = merged["positive_rate"].fillna(50)

    merged["trust_score"] = (
        (merged["rating"] / 5.0) * 60 +
        (merged["positive_rate"] / 100) * 40
    ).round(1)

    def trust_label(score):
        if score >= 75:
            return "🟢 Güvenilir"
        elif score >= 50:
            return "🟡 Orta"
        else:
            return "🔴 Riskli"

    merged["trust_label"] = merged["trust_score"].apply(trust_label)
    return merged


def category_statistics(products):
    return products.groupby("category").agg(
        avg_price=("discounted_price", "mean"),
        median_price=("discounted_price", "median"),
        std_price=("discounted_price", "std"),
        avg_rating=("rating", "mean"),
        product_count=("product_id", "count"),
    ).round(2).reset_index()


def price_history(prices, product_id):
    return prices[prices["product_id"] == product_id].sort_values("month")


def product_sentiment_summary(reviews, product_id):
    prod_reviews = reviews[reviews["product_id"] == product_id]
    if len(prod_reviews) == 0:
        return {"Pozitif": 0, "Negatif": 0, "Nötr": 0}, 0
    counts = prod_reviews["sentiment"].value_counts()
    result = {"Pozitif": 0, "Negatif": 0, "Nötr": 0}
    for k in result:
        result[k] = int(counts.get(k, 0))
    return result, len(prod_reviews)
