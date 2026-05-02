import unittest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis import (
    preprocess, calculate_performance_score, verify_discount,
    seller_trust_analysis, category_statistics, price_history,
    DISCOUNT_FAKE_THRESHOLD, BEST_BUY_SCORE_THRESHOLD, FAIR_SCORE_THRESHOLD
)


def make_products(n=10):
    return pd.DataFrame({
        "product_id": [f"P{i:03d}" for i in range(n)],
        "name": [f"Product {i}" for i in range(n)],
        "category": (["Elektronik", "Giyim"] * n)[:n],
        "seller_id": ["S001"] * n,
        "original_price": np.linspace(100, 1000, n),
        "inflated_price": np.linspace(100, 1000, n) * 1.2,
        "discounted_price": np.linspace(80, 800, n),
        "claimed_discount_rate": [0.30] * n,
        "real_discount_rate": [0.20] * n,
        "rating": np.linspace(2.5, 5.0, n),
        "review_count": np.linspace(10, 3000, n).astype(int),
        "stock": [100] * n,
    })


def make_sellers(n=3):
    return pd.DataFrame({
        "seller_id": [f"S{i:03d}" for i in range(1, n+1)],
        "name": [f"Seller {i}" for i in range(n)],
        "rating": [4.5, 3.0, 2.0][:n],
        "total_sales": [10000, 500, 50][:n],
    })


def make_reviews():
    return pd.DataFrame({
        "review_id": ["R001", "R002", "R003", "R004"],
        "product_id": ["P000", "P001", "P000", "P001"],
        "seller_id": ["S001", "S001", "S002", "S002"],
        "rating": [4.5, 3.0, 5.0, 2.0],
        "sentiment": ["Pozitif", "Negatif", "Pozitif", "Nötr"],
        "text": ["good", "bad", "great", "ok"],
    })


def make_prices():
    return pd.DataFrame({
        "product_id": ["P000"] * 12 + ["P001"] * 12,
        "month": list(range(1, 13)) * 2,
        "price": [100 + i * 5 for i in range(12)] + [200 + i * 3 for i in range(12)],
    })


class TestPreprocess(unittest.TestCase):
    def test_removes_outliers(self):
        products = make_products(20)
        products.loc[0, "discounted_price"] = 999999  # extreme outlier
        out, _ = preprocess(products, make_sellers())
        self.assertFalse((out["discounted_price"] == 999999).any())

    def test_drops_nulls(self):
        products = make_products(5)
        products.loc[2, "rating"] = None
        out, _ = preprocess(products, make_sellers())
        self.assertEqual(out["rating"].isna().sum(), 0)

    def test_returns_dataframe(self):
        out, sellers = preprocess(make_products(), make_sellers())
        self.assertIsInstance(out, pd.DataFrame)
        self.assertIsInstance(sellers, pd.DataFrame)


class TestPerformanceScore(unittest.TestCase):
    def setUp(self):
        self.products = make_products()
        self.sellers = make_sellers()

    def test_score_column_exists(self):
        result = calculate_performance_score(self.products, self.sellers)
        self.assertIn("performance_score", result.columns)

    def test_score_range(self):
        result = calculate_performance_score(self.products, self.sellers)
        self.assertTrue((result["performance_score"] >= 0).all())
        self.assertTrue((result["performance_score"] <= 100).all())

    def test_cluster_label_exists(self):
        result = calculate_performance_score(self.products, self.sellers)
        self.assertIn("cluster_label", result.columns)

    def test_cluster_label_values(self):
        result = calculate_performance_score(self.products, self.sellers)
        valid_labels = {"🏆 Best Buy", "✅ Fair Value", "⚠️ Overpriced"}
        self.assertTrue(set(result["cluster_label"].unique()).issubset(valid_labels))

    def test_high_rating_gets_better_score(self):
        result = calculate_performance_score(self.products, self.sellers)
        high = result[result["rating"] >= 4.5]["performance_score"].mean()
        low = result[result["rating"] <= 3.0]["performance_score"].mean()
        self.assertGreater(high, low)


class TestVerifyDiscount(unittest.TestCase):
    def test_fake_discount_detected(self):
        products = make_products(5)
        products["claimed_discount_rate"] = 0.50
        products["real_discount_rate"] = 0.10  # big gap → fake
        result = verify_discount(products)
        self.assertTrue(result["is_fake_discount"].all())

    def test_real_discount_not_flagged(self):
        products = make_products(5)
        products["claimed_discount_rate"] = 0.20
        products["real_discount_rate"] = 0.18  # tiny gap → real
        result = verify_discount(products)
        self.assertFalse(result["is_fake_discount"].any())

    def test_discount_gap_calculated(self):
        products = make_products(3)
        products["claimed_discount_rate"] = 0.40
        products["real_discount_rate"] = 0.10
        result = verify_discount(products)
        self.assertAlmostEqual(result["discount_gap"].iloc[0], 0.30, places=5)

    def test_verdict_column_exists(self):
        result = verify_discount(make_products())
        self.assertIn("discount_verdict", result.columns)

    def test_threshold_boundary(self):
        products = make_products(2)
        products.loc[0, "claimed_discount_rate"] = 0.30
        products.loc[0, "real_discount_rate"] = 0.30 - DISCOUNT_FAKE_THRESHOLD - 0.01  # just over → fake
        products.loc[1, "claimed_discount_rate"] = 0.30
        products.loc[1, "real_discount_rate"] = 0.30 - DISCOUNT_FAKE_THRESHOLD + 0.01  # just under → real
        result = verify_discount(products)
        self.assertTrue(result.loc[0, "is_fake_discount"])
        self.assertFalse(result.loc[1, "is_fake_discount"])


class TestSellerTrust(unittest.TestCase):
    def test_trust_score_column_exists(self):
        result = seller_trust_analysis(make_sellers(), make_reviews())
        self.assertIn("trust_score", result.columns)

    def test_trust_label_values(self):
        result = seller_trust_analysis(make_sellers(), make_reviews())
        valid = {"🟢 Güvenilir", "🟡 Orta", "🔴 Riskli"}
        self.assertTrue(set(result["trust_label"].unique()).issubset(valid))

    def test_trust_score_range(self):
        result = seller_trust_analysis(make_sellers(), make_reviews())
        self.assertTrue((result["trust_score"] >= 0).all())
        self.assertTrue((result["trust_score"] <= 100).all())


class TestCategoryStatistics(unittest.TestCase):
    def test_columns_present(self):
        result = category_statistics(make_products())
        for col in ["category", "avg_price", "median_price", "std_price", "avg_rating", "product_count"]:
            self.assertIn(col, result.columns)

    def test_product_count_correct(self):
        products = make_products(10)
        result = category_statistics(products)
        total = result["product_count"].sum()
        self.assertEqual(total, 10)

    def test_avg_price_positive(self):
        result = category_statistics(make_products())
        self.assertTrue((result["avg_price"] > 0).all())


class TestPriceHistory(unittest.TestCase):
    def test_filters_correct_product(self):
        prices = make_prices()
        result = price_history(prices, "P000")
        self.assertTrue((result["product_id"] == "P000").all())

    def test_sorted_by_month(self):
        prices = make_prices()
        result = price_history(prices, "P000")
        months = result["month"].tolist()
        self.assertEqual(months, sorted(months))

    def test_empty_for_unknown_product(self):
        prices = make_prices()
        result = price_history(prices, "UNKNOWN")
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
