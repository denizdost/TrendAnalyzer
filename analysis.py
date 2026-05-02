import pandas as pd
import numpy as np

DISCOUNT_FAKE_THRESHOLD = 0.15  # real discount must be at least 15% of claimed
SELLER_TRUST_MIN_SALES = 500
BEST_BUY_SCORE_THRESHOLD = 70
FAIR_SCORE_THRESHOLD = 40


def load_data():
    products = pd.read_csv("data/products.csv")
    sellers = pd.read_csv("data/sellers.csv")
    reviews = pd.read_csv("data/reviews.csv")
    prices = pd.read_csv("data/prices.csv")
    return products, sellers, reviews, prices


def preprocess(products, sellers):
    # Remove outliers using IQR on discounted_price
    Q1 = products["discounted_price"].quantile(0.25)
    Q3 = products["discounted_price"].quantile(0.75)
    IQR = Q3 - Q1
    products = products[
        (products["discounted_price"] >= Q1 - 1.5 * IQR) &
        (products["discounted_price"] <= Q3 + 1.5 * IQR)
    ].copy()
    products = products.dropna()
    return products, sellers


def calculate_performance_score(products, sellers):
    """Compute 0-100 performance score per product."""
    merged = products.merge(sellers, on="seller_id", how="left")

    # Rename to avoid collision after merge
    merged = merged.rename(columns={"rating_x": "rating", "rating_y": "seller_rating"})

    # Normalize rating (0-5 → 0-40 pts)
    merged["rating_score"] = (merged["rating"] / 5.0) * 40

    # Normalize review_count (log scale → 0-30 pts)
    max_log = np.log1p(merged["review_count"].max())
    merged["review_score"] = (np.log1p(merged["review_count"]) / max_log) * 30

    # Seller trust contribution (0-30 pts)
    merged["trust_score"] = (merged["seller_rating"] / 5.0) * 30

    merged["performance_score"] = (
        merged["rating_score"] + merged["review_score"] + merged["trust_score"]
    ).round(1)

    def label(score):
        if score >= BEST_BUY_SCORE_THRESHOLD:
            return "🏆 Best Buy"
        elif score >= FAIR_SCORE_THRESHOLD:
            return "✅ Fair Value"
        else:
            return "⚠️ Overpriced"

    merged["cluster_label"] = merged["performance_score"].apply(label)
    return merged


def verify_discount(products):
    """Flag fake discounts where real discount is much lower than claimed."""
    df = products.copy()
    df["discount_gap"] = df["claimed_discount_rate"] - df["real_discount_rate"]
    df["is_fake_discount"] = df["discount_gap"] > DISCOUNT_FAKE_THRESHOLD
    df["discount_verdict"] = df["is_fake_discount"].map({
        True: "❌ Yanıltıcı İndirim",
        False: "✅ Gerçek İndirim"
    })
    return df


def seller_trust_analysis(sellers, reviews):
    """Compute trust score per seller based on rating + sentiment."""
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
    """Return mean, median, std per category."""
    return products.groupby("category").agg(
        avg_price=("discounted_price", "mean"),
        median_price=("discounted_price", "median"),
        std_price=("discounted_price", "std"),
        avg_rating=("rating", "mean"),
        product_count=("product_id", "count"),
    ).round(2).reset_index()


def price_history(prices, product_id):
    return prices[prices["product_id"] == product_id].sort_values("month")
