# 📊 TrendAnalyzer

> A data-driven dashboard for analyzing Trendyol e-commerce products — scoring performance, detecting fake discounts, evaluating seller trustworthiness, and analyzing customer sentiment.

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
- **Testing:** unittest, coverage.py
- **CI/CD:** GitHub Actions
- **Deployment:** Streamlit Cloud

## 📁 Project Structure

    TrendAnalyzer/
    ├── app.py                  # Main Streamlit application (5 pages)
    ├── analysis.py             # Core analysis engine
    ├── requirements.txt
    ├── data/
    │   ├── generate_data.py    # Synthetic Trendyol dataset generator
    │   ├── products.csv        # 200 products across 8 categories
    │   ├── sellers.csv         # 12 sellers with ratings
    │   ├── reviews.csv         # Customer reviews with sentiment labels
    │   └── prices.csv          # 12-month price history per product
    ├── tests/
    │   └── test_analysis.py    # 22 unit tests — 88% coverage
    └── .github/workflows/
        └── ci.yml              # CI pipeline: lint → test → coverage gate

## 📄 Pages & Features

### 🏠 Dashboard
The landing page provides a market-wide overview of all products. Four KPI cards show total product count, Best Buy products, percentage of misleading discounts, and average performance score. A horizontal bar chart compares average prices across categories, and a donut chart shows product distribution by cluster label (Best Buy, Fair Value, Overpriced). A top-10 table ranks products by performance score.

### 🔍 Product Detail
Search and select any product from a searchable dropdown. The page shows price, rating, performance score, and cluster label. A 12-month price history line chart reveals pricing trends. A sentiment bar chart breaks down reviews into Positive, Neutral, and Negative with a verdict. Discount authenticity is also shown for the selected product.

### 💰 Discount Verification
Exposes misleading discounts by comparing claimed vs. real discount rates. Search for a specific product to see its exact breakdown and verdict. A scatter plot visualizes all products (green = genuine, red = fake). A bar chart shows which categories have the highest rate of misleading discounts.

### 🏪 Seller Trust
Evaluates seller trustworthiness based on rating and positive review rate. Search for a seller to see their trust score, total sales, positive review percentage, and their product list. A scatter chart plots sellers by rating vs. positive review rate, color-coded by trust label. A ranked bar chart shows the top 10 sellers.

### 📈 Category Statistics
Statistical analysis at the category level. Two bar charts compare average prices (with standard deviation) and average ratings across all 8 categories. A summary table shows mean, median, standard deviation, average rating, and product count per category.

## ⚙️ Local Setup

    git clone https://github.com/denizdost/TrendAnalyzer.git
    cd TrendAnalyzer
    pip install -r requirements.txt
    python data/generate_data.py
    streamlit run app.py

## 🧪 Running Tests

    python -m coverage run -m unittest tests/test_analysis.py
    python -m coverage report --include=analysis.py

## 🔬 Analysis Engine

- **Performance Scoring** — Combines product rating (40pts), review count log-scaled (30pts), and seller trust (30pts) into a 0-100 score.
- **Discount Verification** — A gap above 15% between claimed and real discount flags it as misleading.
- **Seller Trust** — Combines seller rating (60%) and positive review rate (40%) into a trust score.
- **Sentiment Analysis** — Classifies reviews as Positive, Negative, or Neutral per product.
- **Category Statistics** — Mean, median, and standard deviation of prices and ratings per category.
