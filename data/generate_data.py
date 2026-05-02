import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)

categories = ["Elektronik", "Giyim", "Ev & Yaşam", "Spor", "Kozmetik", "Kitap", "Oyuncak", "Gıda"]
sellers = [
    {"seller_id": f"S{i:03d}", "name": name, "rating": round(random.uniform(3.0, 5.0), 1), "total_sales": random.randint(100, 50000)}
    for i, name in enumerate(["TechStore", "ModaMart", "EvDepo", "SportZone", "BeautyHub",
                               "KitapSepeti", "OyuncakDünyası", "GıdaMarket", "ElektroShop",
                               "StylePoint", "HomeFirst", "FitLife"], 1)
]

POSITIVE_REVIEWS = [
    "Ürün gerçekten çok iyi, tavsiye ederim.",
    "Harika bir ürün, kalitesi mükemmel.",
    "Çok memnun kaldım, hızlı kargo.",
    "Güzel ve şık, tam istediğim gibiydi.",
    "Kaliteli ürün, fiyatına göre çok değer.",
    "Süper ürün, herkese tavsiye ederim.",
    "Beğendim, sağlam ve kaliteli.",
    "Mükemmeldi, teşekkürler.",
    "Ürün tam açıklandığı gibi, memnunum.",
    "İdeal bir alışveriş, çok rahat.",
]
NEGATIVE_REVIEWS = [
    "Kötü kalite, beklentimi karşılamadı.",
    "Berbat bir ürün, çöp gibi.",
    "Aldatmaca, sahte indirim.",
    "Bozuk geldi, iade ettim.",
    "Kalitesiz, kesinlikle tavsiye etmem.",
    "Hayal kırıklığı, pişman oldum.",
    "Geç geldi ve hasarlıydı.",
    "Ürün yanlış, sorun yaşadım.",
    "Çok kötü, dolandırıcılık gibi.",
    "Beğenmedim, para israfı.",
]
NEUTRAL_REVIEWS = [
    "Fena değil ama daha iyi olabilirdi.",
    "Ortalama bir ürün.",
    "İdare eder.",
    "Ne iyi ne kötü.",
    "Beklediğim gibi çıktı.",
    "Normal, ekstra bir şey yok.",
    "Kullanılabilir durumda.",
    "Fiyatına uygun.",
    "Standart bir ürün.",
    "Sorun yaşamadım.",
]

products = []
for i in range(1, 201):
    cat = random.choice(categories)
    seller = random.choice(sellers)
    original_price = round(random.uniform(50, 5000), 2)
    fake_inflate = random.choice([1.0, 1.0, 1.0, 1.2, 1.5, 2.0])
    inflated_price = round(original_price * fake_inflate, 2)
    discount_rate = round(random.uniform(0.05, 0.60), 2)
    discounted_price = round(inflated_price * (1 - discount_rate), 2)
    real_discount = round(1 - discounted_price / original_price, 2)
    rating = round(random.uniform(2.5, 5.0), 1)
    review_count = random.randint(5, 3000)
    products.append({
        "product_id": f"P{i:03d}",
        "name": f"{cat} Ürün {i}",
        "category": cat,
        "seller_id": seller["seller_id"],
        "original_price": original_price,
        "inflated_price": inflated_price,
        "discounted_price": discounted_price,
        "claimed_discount_rate": discount_rate,
        "real_discount_rate": max(real_discount, 0),
        "rating": rating,
        "review_count": review_count,
        "stock": random.randint(0, 500),
    })

reviews = []
for i, p in enumerate(products):
    for j in range(random.randint(3, 8)):
        sentiment_choice = random.choices(
            ["Pozitif", "Negatif", "Nötr"],
            weights=[0.55, 0.20, 0.25]
        )[0]
        if sentiment_choice == "Pozitif":
            text = random.choice(POSITIVE_REVIEWS)
        elif sentiment_choice == "Negatif":
            text = random.choice(NEGATIVE_REVIEWS)
        else:
            text = random.choice(NEUTRAL_REVIEWS)
        reviews.append({
            "review_id": f"R{i*10+j:04d}",
            "product_id": p["product_id"],
            "seller_id": p["seller_id"],
            "rating": p["rating"] + random.uniform(-0.5, 0.5),
            "sentiment": sentiment_choice,
            "text": text,
        })

prices = []
for p in products:
    for month in range(1, 13):
        prices.append({
            "product_id": p["product_id"],
            "month": month,
            "price": round(p["original_price"] * random.uniform(0.85, 1.30), 2),
        })

pd.DataFrame(products).to_csv("data/products.csv", index=False)
pd.DataFrame(sellers).to_csv("data/sellers.csv", index=False)
pd.DataFrame(reviews).to_csv("data/reviews.csv", index=False)
pd.DataFrame(prices).to_csv("data/prices.csv", index=False)
print("✅ Data generated successfully.")
