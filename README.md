# 📊 TrendAnalyzer

> A data-driven dashboard for analyzing Trendyol e-commerce products — scoring performance, detecting fake discounts, and evaluating seller trustworthiness.

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
- **Containerization:** Docker
- **Deployment:** Streamlit Cloud

## 📁 Project Structure

    TrendAnalyzer/
    ├── app.py                  # Main Streamlit application
    ├── analysis.py             # Core analysis engine
    ├── requirements.txt
    ├── Dockerfile
    ├── data/
    │   ├── generate_data.py    # Synthetic data generator
    │   ├── products.csv
    │   ├── sellers.csv
    │   ├── reviews.csv
    │   └── prices.csv
    ├── tests/
    │   └── test_analysis.py    # 22 unit tests — 88% coverage
    └── .github/workflows/
        └── ci.yml              # CI pipeline (lint → test → coverage gate)

## ⚙️ Local Setup

    git clone https://github.com/denizdost/TrendAnalyzer.git
    cd TrendAnalyzer
    pip install -r requirements.txt
    python data/generate_data.py
    streamlit run app.py

## 🐳 Docker

    docker build -t trendanalyzer .
    docker run -p 8501:8501 trendanalyzer

## 🧪 Running Tests

    python -m coverage run -m unittest tests/test_analysis.py
    python -m coverage report --include=analysis.py

## ✨ Features

- **Dashboard** — KPI cards, category price chart, product cluster distribution
- **Product Analysis** — Price-to-performance scoring (0–100), 12-month price history
- **Discount Verification** — Detects fake vs genuine discounts by comparing claimed vs real discount rates
- **Seller Trust** — Seller rating + positive review rate combined into a trust score
- **Category Statistics** — Mean, median, and standard deviation per product category
