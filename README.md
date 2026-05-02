# 📊 TrendAnalyzer

> Trendyol e-ticaret ürünlerini analiz eden veri odaklı dashboard uygulaması.

[![CI Pipeline](https://github.com/ozhanklnc/TrendAnalyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/ozhanklnc/TrendAnalyzer/actions)

## 🚀 Live Demo

**[https://trendanalyzer.streamlit.app](https://trendanalyzer.streamlit.app)**

## 👥 Takım — StarAI

| İsim | Öğrenci No |
|---|---|
| Deniz Dost | 23070001067 |
| Bora Yıldız | 23070001092 |
| Özhan Kılınç | 22070001031 |
| Atilla Ergin | 23070001058 |

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Testing**: unittest, coverage.py
- **CI/CD**: GitHub Actions
- **Containerization**: Docker
- **Deployment**: Streamlit Cloud

## 📁 Proje Yapısı

```
TrendAnalyzer/
├── app.py                  # Ana Streamlit uygulaması
├── analysis.py             # Çekirdek analiz motoru
├── requirements.txt
├── Dockerfile
├── data/
│   ├── generate_data.py    # Sentetik veri üretici
│   ├── products.csv
│   ├── sellers.csv
│   ├── reviews.csv
│   └── prices.csv
├── tests/
│   └── test_analysis.py    # 22 unit test — %88 coverage
└── .github/workflows/
    └── ci.yml              # CI pipeline
```

## ⚙️ Yerel Kurulum

```bash
git clone https://github.com/ozhanklnc/TrendAnalyzer.git
cd TrendAnalyzer
pip install -r requirements.txt
python data/generate_data.py
streamlit run app.py
```

## 🐳 Docker ile Çalıştırma

```bash
docker build -t trendanalyzer .
docker run -p 8501:8501 trendanalyzer
```

## 🧪 Testleri Çalıştırma

```bash
python -m coverage run -m unittest tests/test_analysis.py
python -m coverage report --include=analysis.py
```

## ✨ Özellikler

- **Dashboard**: KPI kartları, kategori fiyat grafiği, ürün dağılımı
- **Ürün Analizi**: Fiyat-performans skorlaması (0-100), fiyat geçmişi
- **İndirim Doğrulama**: Gerçek vs yanıltıcı indirimleri tespit eder
- **Satıcı Güven**: Satıcı puanı + yorum analizi
- **Kategori İstatistikleri**: Ortalama, medyan, standart sapma
