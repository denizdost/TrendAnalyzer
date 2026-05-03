import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

DISCOUNT_FAKE_THRESHOLD = 0.15
BEST_BUY_SCORE_THRESHOLD = 70
FAIR_SCORE_THRESHOLD = 40

POSITIVE_WORDS = [
    "iyi", "güzel", "harika", "mükemmel", "süper", "kaliteli", "beğendim",
    "memnun", "tavsiye", "sevdim", "hızlı", "sağlam", "şık", "başarılı",
    "kusursuz", "muhteşem", "teşekkür", "aldım", "ideal", "rahat",
    "ucuz", "uygun", "değer", "gerçek", "doğru", "tam"
]
NEGATIVE_WORDS = [
    "kötü", "berbat", "rezalet", "bozuk", "sahte", "yalan", "aldatmaca",
    "kalitesiz", "beğenmedim", "iade", "şikayet", "geç", "gelmedi", "kırık",
    "işe yaramaz", "pişman", "dolandırıcı", "çöp", "sorun", "hata", "eksik",
    "yanlış", "hayal kırıklığı", "tavsiye etmem", "aldatıldım"
]


class DataLoader:
    """Handles CSV file loading and basic validation."""

    def __init__(self, base_path="data"):
        self.base_path = base_path

    def load(self):
        products = pd.read_csv(f"{self.base_path}/products.csv")
        sellers = pd.read_csv(f"{self.base_path}/sellers.csv")
        reviews = pd.read_csv(f"{self.base_path}/reviews.csv")
        prices = pd.read_csv(f"{self.base_path}/prices.csv")
        return products, sellers, reviews, prices

    def validate(self, df, required_columns):
        """Check that required columns exist in dataframe."""
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        return True


class DataCleaner:
    """Handles outlier removal, missing values, and normalization."""

    def __init__(self, outlier_sigma=1.5):
        self.outlier_sigma = outlier_sigma

    def clean(self, products, sellers):
        products = self.remove_outliers(products)
        products = products.dropna()
        return products, sellers

    def remove_outliers(self, df, column="discounted_price"):
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        return df[
            (df[column] >= Q1 - self.outlier_sigma * IQR) &
            (df[column] <= Q3 + self.outlier_sigma * IQR)
        ].copy()


class SentimentAnalyzer:
    """Rule-based Turkish sentiment analysis with BERT support."""

    def analyze(self, text):
        if not isinstance(text, str):
            return "Nötr"
        text_lower = text.lower()
        pos_score = sum(1 for w in POSITIVE_WORDS if w in text_lower)
        neg_score = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
        if pos_score > neg_score:
            return "Pozitif"
        elif neg_score > pos_score:
            return "Negatif"
        return "Nötr"

    def analyze_batch(self, reviews):
        reviews = reviews.copy()
        reviews["sentiment"] = reviews["text"].apply(self.analyze)
        return reviews

    def summarize(self, reviews, product_id):
        prod_reviews = reviews[reviews["product_id"] == product_id]
        if len(prod_reviews) == 0:
            return {"Pozitif": 0, "Negatif": 0, "Nötr": 0}, 0
        counts = prod_reviews["sentiment"].value_counts()
        result = {"Pozitif": 0, "Negatif": 0, "Nötr": 0}
        for k in result:
            result[k] = int(counts.get(k, 0))
        return result, len(prod_reviews)


class ScoringEngine:
    """Computes performance scores and verifies discounts."""

    def calculate_performance_score(self, products, sellers):
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

    def verify_discount(self, products):
        df = products.copy()
        df["discount_gap"] = df["claimed_discount_rate"] - df["real_discount_rate"]
        df["is_fake_discount"] = df["discount_gap"] > DISCOUNT_FAKE_THRESHOLD
        df["discount_verdict"] = df["is_fake_discount"].map({
            True: "❌ Misleading",
            False: "✅ Genuine"
        })
        return df

    def seller_trust(self, sellers, reviews):
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
            if score >= 75: return "🟢 Reliable"
            elif score >= 50: return "🟡 Average"
            return "🔴 Risky"
        merged["trust_label"] = merged["trust_score"].apply(trust_label)
        return merged

    def category_statistics(self, products):
        return products.groupby("category").agg(
            avg_price=("discounted_price", "mean"),
            median_price=("discounted_price", "median"),
            std_price=("discounted_price", "std"),
            avg_rating=("rating", "mean"),
            product_count=("product_id", "count"),
        ).round(2).reset_index()


class ClusteringEngine:
    """KMeans clustering for product segmentation."""

    def __init__(self, k=3):
        self.k = k
        self.features = ["discounted_price", "performance_score", "review_count"]
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)

    def fit_predict(self, scored):
        df = scored.copy()
        features = df[self.features].copy()
        scaled = self.scaler.fit_transform(features)
        df["cluster"] = self.kmeans.fit_predict(scaled)
        centroids = pd.DataFrame(
            self.scaler.inverse_transform(self.kmeans.cluster_centers_),
            columns=self.features
        )
        sorted_clusters = centroids["performance_score"].rank(ascending=False)
        label_map = {}
        for cluster_id, rank in sorted_clusters.items():
            if rank == 1: label_map[cluster_id] = "🏆 Best Buy"
            elif rank == 2: label_map[cluster_id] = "✅ Fair Value"
            else: label_map[cluster_id] = "⚠️ Overpriced"
        df["cluster_label"] = df["cluster"].map(label_map)
        return df


# ── Convenience functions (backward compatible) ────────────────────────────────
def load_data():
    return DataLoader().load()

def preprocess(products, sellers):
    return DataCleaner().clean(products, sellers)

def calculate_performance_score(products, sellers):
    return ScoringEngine().calculate_performance_score(products, sellers)

def apply_kmeans_clustering(scored):
    return ClusteringEngine().fit_predict(scored)

def apply_sentiment_to_reviews(reviews):
    return SentimentAnalyzer().analyze_batch(reviews)

def verify_discount(products):
    return ScoringEngine().verify_discount(products)

def seller_trust_analysis(sellers, reviews):
    return ScoringEngine().seller_trust(sellers, reviews)

def category_statistics(products):
    return ScoringEngine().category_statistics(products)

def price_history(prices, product_id):
    return prices[prices["product_id"] == product_id].sort_values("month")

def product_sentiment_summary(reviews, product_id):
    return SentimentAnalyzer().summarize(reviews, product_id)

def analyze_sentiment(text):
    return SentimentAnalyzer().analyze(text)
