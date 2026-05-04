# 📊 TrendAnalyzer

> A data-driven dashboard for analyzing Trendyol e-commerce products — scoring performance, detecting fake discounts, evaluating seller trustworthiness, and analyzing customer sentiment using real ML models.

[![CI Pipeline](https://github.com/denizdost/TrendAnalyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/denizdost/TrendAnalyzer/actions)

## 🚀 Live Demo

**[https://trendanalyzer-0.streamlit.app](https://trendanalyzer-0.streamlit.app)**

## 👥 Team — StarAI

| Name | Student ID |
|---|---|
| Deniz Dost | 23070001067 |
| Bora Yıldız | 23070001092 |
| Özhan Kılınç | 22070001031 |
| Atilla Ergin | 23070001058 |
| Çağan Özdamar | 23070001089 |

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly
- **ML — Clustering:** scikit-learn (KMeans)
- **ML — Sentiment:** Rule-based Turkish NLP + BERT (savasy/bert-base-turkish-sentiment-cased)
- **Testing:** unittest, coverage.py
- **CI/CD:** GitHub Actions
- **Deployment:** Streamlit Cloud

## 📁 Project Structure

    TrendAnalyzer/
    ├── app.py                  # Main Streamlit application (5 pages)
    ├── analysis.py             # Core analysis engine (KMeans, sentiment, scoring)
    ├── requirements.txt
    ├── Dockerfile
    ├── data/
    │   ├── generate_data.py    # Synthetic Trendyol dataset generator
    │   ├── products.csv        # 200 products across 8 categories
    │   ├── sellers.csv         # 12 sellers with ratings
    │   ├── reviews.csv         # Turkish customer reviews with sentiment labels
    │   └── prices.csv          # 12-month price history per product
    ├── tests/
    │   └── test_analysis.py    # 22 unit tests — 88% coverage
    └── .github/workflows/
        └── ci.yml              # CI pipeline: lint → test → coverage gate

## 📄 Pages & Features

### 🏠 Dashboard
Market-wide overview with four KPI cards (total products, Best Buy count, misleading discount rate, average performance score). Horizontal bar chart compares average prices across categories. Donut chart shows product distribution by KMeans cluster label. Top-10 table with CSV export.

### 🔍 Product Detail
Searchable product dropdown. Shows price, rating, performance score, and KMeans cluster label with the three features used. 12-month price history chart. Review sentiment breakdown with verdict. Live BERT sentiment analyzer — type any Turkish review and get real-time classification from both rule-based and BERT models side by side. Discount authenticity check.

### 💰 Discount Verification
Detects misleading discounts by comparing claimed vs. real discount rates. Search for a specific product to see exact breakdown and verdict. Scatter plot (green = genuine, red = fake). Bar chart of misleading discount rates by category.

### 🏪 Seller Trust
Evaluates sellers based on rating and positive review rate combined into a trust score. Search for a seller to see their metrics and full product list. Scatter plot and top 10 ranking.

### 📈 Category Statistics
Statistical analysis per category: average price with standard deviation, average rating, product count.

## 🤖 ML Pipeline

### KMeans Clustering
Products clustered into 3 segments using sklearn KMeans with StandardScaler normalization on: discounted price, performance score, and review count. Labels: Best Buy, Fair Value, Overpriced.

### Sentiment Analysis
Two-layer approach: rule-based Turkish keyword analysis (~90% accuracy) for batch processing, and BERT (savasy/bert-base-turkish-sentiment-cased) for live user input analysis.

### Performance Scoring
0-100 score: product rating (40pts) + log-scaled review count (30pts) + seller trust (30pts).

### Discount Verification
A gap above 15% between claimed and real discount flags it as misleading.

## ⚙️ Local Setup

    git clone https://github.com/denizdost/TrendAnalyzer.git
    cd TrendAnalyzer
    pip install -r requirements.txt
    python data/generate_data.py
    streamlit run app.py

## 🧪 Running Tests

    python -m coverage run -m unittest tests/test_analysis.py
    python -m coverage report --include=analysis.py
# CI trigger
